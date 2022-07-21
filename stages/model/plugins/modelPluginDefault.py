from stages.model import ModelPluginInterface
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from database import DatabaseHandler
import pandas as pd
from type import Type


class Plugin(ModelPluginInterface):
    """
    This plugin uses Logistic Regression to detect attacks

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
        Initial method with basic attributes
        """
        # Dict to save the trained models for the Factory pattern
        self.model_dict = {}
        # List of keys which refers to a quantitative feature
        self.quant_keys = ["length", "basic_feature_count", "path_feature_count", "path_query_lower",
                           "path_query_upper", "path_query_numeric", "path_query_spaces", "path_query_specialchar",
                           "query_monograms", "query_bigrams", "query_hexagrams"]

    def get_model(self, type: Type) -> object:
        """
        Factory method which returns an existing Instance of the LogisticRegressionClass or creates a new if no
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
            self.model_dict[type] = LogisticRegressionClass()
        # Return the requested Instance
        return self.model_dict[type]


    def set_model(self, db_handler: DatabaseHandler) -> None:
        """
        This model initialises the Factory method

        Parameters
        ----------
        db_handler: DatabaseHandler
            This variable contains the connection to the database handling class
        """

        # Read available Factory from the database
        model_dict = db_handler.get_object("lr_model_dict")
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
        print("Train_Model")
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
            db_handler.write_object("lr_model_dict", self.model_dict)
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
        # Get all quantitative features
        dict_quant_features = [{item: predicting_data.get(item) for item in self.quant_keys}]
        # Call the ML-Model and return the result
        return self.get_model(type).predict(dict_quant_features)


class LogisticRegressionClass:
    """
    This Class contains a Logistic Regression Model for a specific type

    Attributes
    ----------
    model: Pipeline
        The ML-Model of the current instance
    score: int
        The accuracy score of the current model
    trained: bool
        Boolean variable if the current model is already trained and ready to predict attacks

    Methods
    ----------
    train_model(training_data, training_labels)
        This method trains the ML-Model with the given input data
    predict(predicting_data)
        This method makes a prediction with the pretrained ML-Model for the given input vector
    """

    def __init__(self):
        """
        Initial method with basic attributes
        """
        # Empty ML-Model
        self.model = Pipeline([('scaler', StandardScaler()), ('lr', LogisticRegression(random_state=0))])
        # Set initial accuracy to zero
        self.score = 0
        # Set initial model as not trained
        self.trained = False

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
        # Create Train / Test split with 20 % Test data to validate the trained model
        x_train_set, x_test_set, y_train_labels, y_test_labels = train_test_split(df_training_data, training_labels,
                                                                                  test_size=0.2, random_state=22)
        # Create local Copy of the ML-Model
        model = self.model
        # Train the Model
        model.fit(x_train_set, y_train_labels)
        # Predict for the test set
        model.predict(x_test_set)
        # Check if the new score of the model is better than the last
        if self.score < model.score(x_test_set, y_test_labels):
            # Safe the new model and score
            self.score = model.score(x_test_set, y_test_labels)
            self.model = model
            self.trained = True
        print(self.score)

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
        if self.trained:
            # Predict and return the result and accuracy
            print(predicting_data)
            df_predicting_data = pd.DataFrame(predicting_data)
            return [self.model.predict(df_predicting_data)[0], self.model.predict_proba(df_predicting_data)[0][1]]
        else:
            # If the model is not trained return always an attack with 100 %
            return [1, 1]
