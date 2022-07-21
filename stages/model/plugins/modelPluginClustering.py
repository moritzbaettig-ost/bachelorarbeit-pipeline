from sklearn.cluster import KMeans
from stages.model import ModelPluginInterface
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from database import DatabaseHandler
import pandas as pd
import threading
from type import Type


class Plugin(ModelPluginInterface):
    """
    This plugin uses KMeans Clustering to detect attacks

    Attributes
    ----------
    model_dict: dict
        Dictionary for the factory method which contains for each available type a trained ML-Model
    quant_keys: list
        List of quantified features which can be used for the ML-Model

    Methods
    ----------
    get_model(type)
        Returns a LogisticRegressionClass with a trained ML-Model for a specific type.
    set_model(db_handler)
        Loads the pretrained LogisticRegressionClasses dict for the factory method from the database.
    train_model(type, db_handler)
        Trains the ML-Model in the LogisticRegressionClass for a specific type with all available data from the database.
    predict(type, predicting_data)
        Predicts if a feature vector belongs to an attack or not.
    """

    def __init__(self):
        """
        Initial method whit basic attributes
        """

        # Dict to save the trained models for the Factory pattern
        self.model_dict = {}
        # List of keys which refers to a quantitative feature
        self.quant_keys = ["length", "basic_feature_count", "path_feature_count", "path_query_lower",
                           "path_query_upper", "path_query_numeric", "path_query_spaces", "path_query_specialchar",
                           "query_monograms", "query_bigrams", "query_hexagrams"]

    def get_model(self, type: Type) -> object:
        """
        Factory methode which returns an existing Instance of the LogisticRegressionClass or creates a new if no
        Instance exists for a specific type

        Parameters
        ----------
        type: Type
            The type parameter specifies the Type of the request and the requested resource

        Returns
        ----------
        object
            Returns the corresponding Instance of the LogisticRegressionClass to a specific type
        """
        # Check if the Factory contains an Instance of the LogisticRegressionClass for a specific type
        if type not in self.model_dict:
            # Create a new Instance
            self.model_dict[type] = KMeansClass()
        # Return the requested Instance
        return self.model_dict[type]


  def set_model(self, db_handler: DatabaseHandler) -> None:
        """
        This model initialises the factory pattern

        Parameters
        ----------
        db_handler: DatabaseHandler
            This variable contains the connection to the database handling class
        """
        
        # Read available Factory from the database
        model_dict = db_handler.get_object("kMeans_model_dict")
        # Check if a Factory dict was available in the database
        if model_dict is not False:
            # Check if the factory is corrupt
            if len(model_dict) > 0:
                self.model_dict = model_dict


    def train_model(self, type: Type, db_handler: DatabaseHandler) -> None:
        """
        This method reads the required features from the database and trains the Logistic Regression Model

        Parameters
        ----------
        db_handler: DatabaseHandler
            This variable contains the connection to the database handling class
        """

        db_data = db_handler.get_object("data")
        db_data_actual_type = []
        count_attack = 0
        count_no_attack = 0
        # Chose the required features for the actual type
        for d in db_data:
            if d['type'] == type:
                db_data_actual_type.append(d)
                if d['label'] == 0:
                    count_no_attack = count_no_attack + 1
                elif d['label'] == 1:
                    count_attack = count_attack + 1
        # Check if enough reference data are available to train the model
        if len(db_data_actual_type) > 5 and count_no_attack > 2 and count_attack > 2:
            training_data = []
            for d in db_data_actual_type:
                training_data.append({item: d['features'].get(item) for item in self.quant_keys})
            training_labels = [d['label'] for d in db_data_actual_type]
            self.get_model(type).train_model(training_data, training_labels)
            thread = threading.Thread(target=db_handler.write_object, args=("kMeans_model_dict", self.model_dict))
            thread.start()
        else:
            print("Not enough Data available for " + type.path)

    def predict(self, type: Type, predicting_data: dict) -> list:
        """
        Predict if a request is an attack

        Parameters
        ----------
        type: Type
            The type parameter specifies the Type of the request and the requested resource
        predicting_data: dict
            The predicting_data dictionary is the feature vector of the current request which needs to be predicted
        Returns
        ----------
        list
            Returns a list of the pattern [attack (1)/no attack(0), probability of the attack]
        """
        
        dict_quant_features = [{item: predicting_data.get(item) for item in self.quant_keys}]
        return self.get_model(type).predict(dict_quant_features)


class KMeansClass:
    """
    This Class contains a KMeans Model for a specific type

    Attributes
    ----------
    num_of_clusters: int
        Defines the number of clusters for the Clustering
    model: Pipeline
        The ML-Model of the current instance
    score: int
        The accuracy score of the current model
    trained: bool
        Boolean variable if the current model is already trained and ready to predict attacks
    alert_clusters: list
        Contains all Clusters with group attacks

    Methods
    ----------
    train_model(training_data, training_labels)
        This method trains the ML-Model with the given input data
    predict(predicting_data)
        This method makes a prediction with the pretrained ML-Model for the given input vector
    """

    def __init__(self):
        """
        Initial method whit basic attributes
        """

        # Empty ML-Model
        print("KMeanClass Created")
        # Number of clusters
        self.num_of_clusters = 6
        self.model = Pipeline([('scaler', StandardScaler()), ('KMeans', KMeans(
            n_clusters=self.num_of_clusters, init='random',
            n_init=10, max_iter=300,
            tol=1e-04, random_state=0
        ))])
        # Set initial accuracy to zero
        self.score = 0
        # Set initial model as not trained
        self.trained = False
        self.alert_clusters = []

    def train_model(self, training_data: list, training_labels: list) -> None:
        """
        This method trains the logistic regression model with the available data

        Parameters
        ----------
        training_data: list
            Is a list of dict objects fom all available reference data
        training_labels: list
            Is a list of all labels corresponding to the training_data list
        """
        # Create Pandas Dataframe from the reference Data
        df_training_data = pd.DataFrame(training_data)
        # Create local Copy of the ML-Model
        model = self.model
        # Train the Model
        model.fit(df_training_data)
        # Predict for the test set
        df_training_data = df_training_data.assign(predicted_cluster=model.predict(df_training_data))
        df_training_data = df_training_data.assign(labels=training_labels)
        # Check if the new score of the model is better than the last
        clusters = []
        for i in range(self.num_of_clusters):
            clusters.append([
                df_training_data[(df_training_data.labels < 1) & (df_training_data.predicted_cluster == i)].shape[0],
                df_training_data[(df_training_data.labels > 0) & (df_training_data.predicted_cluster == i)].shape[0]])

        self.alert_clusters = []
        for i in range(self.num_of_clusters):
            if clusters[i][0] < clusters[i][1]:
                self.alert_clusters.append(i)
        print("Alert_Clusters")
        print(self.alert_clusters)

        self.trained = True
        self.model = model

    def predict(self, predicting_data: list) -> list:
        """
        This method predicts if a request is an attack or not

        Parameters
        ----------
        predicting_data: list
            Is the feature vector which needs to be predicted as attack or not

        Returns
        ----------
        list
            Returns a list of the pattern [attack (1)/no attack(0), probability of the attack]
        """
        # Check if the model is trained
        print("Cluster Prediction")
        if self.trained:
            # Predict and return the result and accuracy
            print("Cluster")
            df_predicting_data = pd.DataFrame(predicting_data)
            print(self.model.predict(df_predicting_data))
            if self.model.predict(df_predicting_data)[0] in self.alert_clusters:
                return [1, 1]
            else:
                return [0, 0]
            # return [self.model.predict(df_predicting_data)[0], self.model.predict_proba(df_predicting_data)[0][1]]
        else:
            # If the model is not trained return always an attack with 100 %
            return [1, 1]
