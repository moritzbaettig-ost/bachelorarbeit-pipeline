#%%
import copy
import warnings
import random
import numpy as np
import matplotlib.pyplot as plt
import sklearn
from sklearn import metrics
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import silhouette_score, ConfusionMatrixDisplay
from sklearn.model_selection import learning_curve, train_test_split
from sklearn.model_selection import ShuffleSplit
import ZODB, ZODB.FileStorage, ZODB.DB
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from gap_statistic import OptimalK
import seaborn as sns


class HelperDataClass:
    """
    The HelperDataClass contains the connection to the Database.

    Attributes
    ----------
        db: ZODB
            Contains the reference to th ZODB Database
        data: pandas DataFrame
            Contains all Data from the Database in a Pandas DataFrame
    """

    def __init__(self):
        """
        Initial method with basic attributes
        """

        # Connection to the ZODB
        storage = ZODB.FileStorage.FileStorage('db.fs')
        self.db = ZODB.DB(storage)
        connection = self.db.open()
        root = connection.root()
        self.data = pd.DataFrame()
        # Check if object exists in root namespace
        if "data" in root:
            # Copy the object from the database
            obj = copy.deepcopy(root["data"])
            # Store Data From the Database in Dataframe
            self.data = pd.DataFrame(dict(obj).values())
        else:
            # Return False if the object does not exist in the database
            obj = False
        connection.close()
        self.db.close()


    def count_labels_per_type(self):
        """
        Counts the labels per type and prints a list for every type in the form [# normal, # anomaly]
        """

        counter_dict = {}
        for index, row in self.data.iterrows():
            if row["type"] not in counter_dict:
                counter_dict[row["type"]] = [0, 0]
            else:
                counter_dict[row["type"]][row["label"]] += 1
        for key, value in counter_dict.items():
            print(key)
            print(f"# of Requests in Data: {value}\n")


class HelperLogRegressionPerfAnalytics:
    """
    Class to Analyse the Logistic Regression Performance

    Attributes
    ----------
        helperData: HelperDataClass
            Contains a reference to the HelperDataClass

    Methods
    ----------
        plot_learning_curve()
            Returns a Plot of the Learning Curve from a ML Modell
        evaluate_log_Regression()
            This Function evaluates the Score of a Logistic Regression Model
        get_conf_matrix
            This Function returns two Plots. One of the Confusion Matrix and an other of the normalized confusin Matrix.
    """

    def __init__(self, helperData: HelperDataClass):
        """
        Initial method with basic attributes
        """
        self.helperData = helperData

    def plot_learning_curve(self, estimator, title, X, y, axes=None, ylim=None, cv=None, n_jobs=None,
                            train_sizes=np.linspace(0.1, 1.0, 5)):
        """
        Generate 3 plots: the test and training learning curve, the training
        samples vs fit times curve, the fit times vs score curve.

        Parameters
        ----------
        estimator : estimator instance
            An estimator instance implementing `fit` and `predict` methods which
            will be cloned for each validation.

        title : str
            Title for the chart.

        X : array-like of shape (n_samples, n_features)
            Training vector, where ``n_samples`` is the number of samples and
            ``n_features`` is the number of features.

        y : array-like of shape (n_samples) or (n_samples, n_features)
            Target relative to ``X`` for classification or regression;
            None for unsupervised learning.

        ylim : tuple of shape (2,), default=None
            Defines minimum and maximum y-values plotted, e.g. (ymin, ymax).

        cv : int, cross-validation generator or an iterable, default=None
            Determines the cross-validation splitting strategy.
            Possible inputs for cv are:

              - None, to use the default 5-fold cross-validation,
              - integer, to specify the number of folds.
              - :term:`CV splitter`,
              - An iterable yielding (train, test) splits as arrays of indices.

            For integer/None inputs, if ``y`` is binary or multiclass,
            :class:`StratifiedKFold` used. If the estimator is not a classifier
            or if ``y`` is neither binary nor multiclass, :class:`KFold` is used.

            Refer :ref:`User Guide <cross_validation>` for the various
            cross-validators that can be used here.

        n_jobs : int or None, default=None
            Number of jobs to run in parallel.
            ``None`` means 1 unless in a :obj:`joblib.parallel_backend` context.
            ``-1`` means using all processors. See :term:`Glossary <n_jobs>`
            for more details.

        train_sizes : array-like of shape (n_ticks,)
            Relative or absolute numbers of training examples that will be used to
            generate the learning curve. If the ``dtype`` is float, it is regarded
            as a fraction of the maximum size of the training set (that is
            determined by the selected validation method), i.e. it has to be within
            (0, 1]. Otherwise it is interpreted as absolute sizes of the training
            sets. Note that for classification the number of samples usually have
            to be big enough to contain at least one sample from each class.
            (default: np.linspace(0.1, 1.0, 5))
        """

        if axes is None:
            _, axes = plt.subplots(figsize=(10, 10))

        plt.title(title)
        if ylim is not None:
            plt.ylim(*ylim)
        plt.xlabel("Training examples")
        plt.ylabel("Score")

        train_sizes, train_scores, test_scores, fit_times, _ = learning_curve(estimator, X, y, cv=cv, n_jobs=n_jobs,
                                                                              train_sizes=train_sizes,
                                                                              return_times=True)
        train_scores_mean = np.mean(train_scores, axis=1)
        train_scores_std = np.std(train_scores, axis=1)
        test_scores_mean = np.mean(test_scores, axis=1)
        test_scores_std = np.std(test_scores, axis=1)

        # Plot learning curve
        plt.grid()
        plt.fill_between(
            train_sizes,
            train_scores_mean - train_scores_std,
            train_scores_mean + train_scores_std,
            alpha=0.1,
            color="r",
        )
        plt.fill_between(
            train_sizes,
            test_scores_mean - test_scores_std,
            test_scores_mean + test_scores_std,
            alpha=0.1,
            color="g",
        )
        plt.plot(
            train_sizes, train_scores_mean, "o-", color="r", label="Training score"
        )
        plt.plot(
            train_sizes, test_scores_mean, "o-", color="g", label="Cross-validation score"
        )
        plt.legend(loc="best")
        return plt

    def evaluate_log_Regression(self):
        """
        This Function evaluates the Score of an ML-Modell and calls the plot_learning_curve Function
        """

        # Get a list of unique Types
        num_of_types = self.helperData.data['type'].unique()
        num_of_plots = 0
        types = []

        for t in num_of_types:
            # Check if enough data is available for the Model
            if len(self.helperData.data.loc[self.helperData.data['type'] == t]) > 200:
                num_of_plots = num_of_plots + 1
                types.append(t)

        for type in types:
            if type.path == '/tienda1/miembros/editar.jsp' and type.method == 'GET' and type.has_query==True and type.has_body==False:
                # Get Feature Data
                X = self.helperData.data.loc[self.helperData.data['type'] == type]['features']
                # Get Labels
                y = self.helperData.data.loc[self.helperData.data['type'] == type]['label']
                title = "Learning Curves\n" + type.path
                # Cross validation with 50 iterations to get smoother mean test and train
                # score curves, each time with 20% data randomly selected as a validation set.
                cv = ShuffleSplit(n_splits=50, test_size=0.2, random_state=0)
                estimator = Pipeline([('scaler', StandardScaler()), ('lr', LogisticRegression(random_state=0))])
                # Parse Dict to Dataframe
                features = pd.DataFrame(dict(X).values())
                # Plot the Learning Curve for the Data
                self.plot_learning_curve(estimator, title, features, y, ylim=(0.0, 1.01), cv=cv, n_jobs=4)
            plt.show()

    def get_conf_matrix(self):
        """
        This Function plots the Confusion Matrix in absolute and normalized values
        """

        for type in self.helperData.data['type'].unique():
            # Choose a specific Type
            if type.path == '/tienda1/miembros/editar.jsp' and type.method == 'GET' and type.has_query==True and type.has_body==False:
                # Get Feature Data Fram PD DataFrame
                X = self.helperData.data.loc[self.helperData.data['type'] == type]['features']
                # Parse dict Values to DataFrame
                X = pd.DataFrame(dict(X).values())
                # Get Labels
                y = self.helperData.data.loc[self.helperData.data['type'] == type]['label']
                y = pd.DataFrame(dict(y).values())
                # Split the data into a training set and a test set
                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=22)
                model = Pipeline([('scaler', StandardScaler()), ('lr', LogisticRegression(random_state=0))])
                print(type)
                print("Labels")
                print(y_train)
                model.fit(X_train, y_train)

                np.set_printoptions(precision=2)

                # Plot non-normalized confusion matrix
                titles_options = [
                    ("Confusion matrix, without normalization", None),
                    ("Normalized confusion matrix", "true"),
                ]
                for title, normalize in titles_options:
                    disp = ConfusionMatrixDisplay.from_estimator(
                        model,
                        X_test,
                        y_test,
                        cmap=plt.cm.Blues,
                        normalize=normalize,
                    )
                    disp.ax_.set_title(title)

                plt.show()

    def get_distance_distribution(self):
        # https://medium.com/geekculture/essential-guide-to-handle-outliers-for-your-logistic-regression-model-63c97690a84d
        for type in self.helperData.data['type'].unique():
            # Choose a specific Type
            if type.path == '/tienda1/miembros/editar.jsp' and type.method == 'GET' and type.has_query==True and type.has_body==False:
                # Get Feature Data Fram PD DataFrame
                X = self.helperData.data.loc[self.helperData.data['type'] == type]['features']
                # Parse dict Values to DataFrame
                X = pd.DataFrame(dict(X).values())
                # Get Labels
                y = self.helperData.data.loc[self.helperData.data['type'] == type]['label']
                y = pd.DataFrame(dict(y).values())
                scaler = StandardScaler()
                scaler.fit(X)
                X = scaler.transform(X)
                # Split the data into a training set and a test set
                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=22)
                model = LogisticRegression(random_state=0)
                model.fit(X_train, y_train)
                weight_vector = list(model.coef_[0])
                dist = np.dot(X_train, weight_vector)
                y_dist = dist * [-1 if x == 0 else 1 for x in list(y_train)]
                # Choose 10 % quantil
                val_under = np.percentile(y_dist, 5)
                # Choose 90 % quantil
                val_upper = np.percentile(y_dist, 95)

                sns.kdeplot(y_dist)
                #plt.axvline(val_under, linestyle="--")
                #plt.axvline(val_upper, linestyle="--")
                plt.xlabel("Distance * Y-class")
                plt.title("Verteilung der Distanzen")
                plt.grid()
                plt.show()

                # Fit the data to a logistic regression model.
                pca = PCA(n_components=2)
                pca.fit(X_train)
                X_train = pd.DataFrame(pca.transform(X_train))
                clf = sklearn.linear_model.LogisticRegression()
                clf.fit(X_train, y_train)

                # Retrieve the model parameters.
                b = clf.intercept_[0]
                w1, w2 = clf.coef_[0].T
                # Calculate the intercept and gradient of the decision boundary.
                c = -b / w2
                m = -w1 / w2

                X_attack =[]
                X_no_attack = []
                dist_outlier = []
                i=0
                y_train = np.array(y_train)
                for x in X_train.to_numpy():
                    if y_dist[i]<val_under or y_dist[i]>val_upper:
                        dist_outlier.append(x)
                    if y_train[i]==0:
                        X_no_attack.append(x)
                    else:
                        X_attack.append(x)
                    i = i+1
                # Plot the data and the classification with the decision boundary.
                xmin, xmax = -5, 6
                ymin, ymax = -4, 4
                xd = np.array([xmin, xmax])
                yd = m * xd + c
                plt.plot(xd, yd, 'k', lw=1, ls='--')
                plt.fill_between(xd, yd, ymin, color='tab:blue', alpha=0.2)
                plt.fill_between(xd, yd, ymax, color='tab:orange', alpha=0.2)

                print("All detected Outliers")
                print(np.array(dist_outlier)[:, 0])
                print(np.array(dist_outlier)[:, 1])
                print("All detected Outliers")
                plt.scatter(np.array(X_no_attack)[:,0],np.array(X_no_attack)[:,1], s=8, alpha=0.5,label = 'NoAttack')
                plt.scatter(np.array(X_attack)[:,0], np.array(X_attack)[:,1], s=8, alpha=0.5, label = 'Attack')
                plt.scatter(np.array(dist_outlier)[:, 0], np.array(dist_outlier)[:, 1], s=20, facecolors='none', edgecolors='r', label='Leverage Point')
                plt.legend()
                plt.xlim(xmin, xmax)
                plt.ylim(ymin, ymax)
                plt.title("Decision Boundary after PCA")
                plt.ylabel(r'$x_2$')
                plt.xlabel(r'$x_1$')

                plt.show()


class HelperKMeansPerfAnalytics:
    """
    The HelperKMeansPerfAnalytics Class analyzes the Performance and number of Clusters for the KMeans Algorithms

    Attributes
    ----------
    helperData: HelperDataClass
        Contains a reference to the HelperDataClass

    Methods
    ----------
    eval_num_of_cluster()
        Plots the SSE, SS and Gap-Stat Graph for the given Number of Clusters
    KMeans_clustering_func()
        Helper Function for the Gap-Stat Method
    guete_function()
        Plots the Graph for the Gütefunktion of the Clusters
    """

    def __init__(self, helperData: HelperDataClass):
        """
        Initial method with basic attributes
        """
        self.helperData = helperData

    def eval_num_of_cluster(self):
        """
        This Function Plots the SSE, SS and Gap-Stat Function
        """

        # Read Unique Type from Database
        for type in self.helperData.data['type'].unique():
            # Set a specific Path
            if type.path == '/tienda1/miembros/editar.jsp' and type.method == 'GET' and type.has_query==True and type.has_body==False:
                # Get Features from Dataframe
                X = self.helperData.data.loc[self.helperData.data['type'] == type]['features']
                # Parse Dict to DataFrame
                X = pd.DataFrame(dict(X).values())
                #Normalize the Data
                scaler = StandardScaler()
                scaler.fit(X)
                X = scaler.transform(X)

                # Get Labels from Dataframe
                cluster_labels = self.helperData.data.loc[self.helperData.data['type'] == type]['label']
                clusters = 15
                elbow = []
                ss = []
                # For different number of cluster
                for n_clusters in range(2, clusters):
                    # iterating through cluster sizes
                    clusterer = KMeans(n_clusters=n_clusters, init='random', n_init=10, max_iter=300, tol=1e-04,
                                       random_state=0)
                    cluster_labels = clusterer.fit_predict(X)
                    # Finding the average silhouette score
                    silhouette_avg = silhouette_score(X, cluster_labels)
                    ss.append(silhouette_avg)
                    print("For n_clusters =", n_clusters, "The average silhouette_score is :", silhouette_avg)
                    # Finding the average SSE"
                    elbow.append(
                        clusterer.inertia_)  # Inertia: Sum of distances of samples to their closest cluster center

                # --------------------create a wrapper around OptimalK to extract cluster centers and cluster labels
                optimalK = OptimalK(n_jobs=1, clusterer=self.KMeans_clustering_func)
                # --------------------Run optimal K on the input data (subset_scaled_interim) and number of clusters
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    n_clusters = optimalK(X, cluster_array=np.arange(1, 15))
                print('Optimal clusters: ', n_clusters)
                # --------------------Gap Statistics data frame
                optimalK.gap_df[['n_clusters', 'gap_value']]

                fig = plt.figure(figsize=(21, 7))
                n_clusters = 6
                fig.add_subplot(131)
                plt.plot(range(2, clusters), elbow, 'b-', label='Sum of squared error')
                plt.scatter(n_clusters,
                            elbow[n_clusters - 2], s=250, c='r')
                plt.grid(True)
                plt.axvline(n_clusters, linestyle="--")
                plt.title('SSE by Cluster Count')
                plt.xlabel("Number of cluster")
                plt.ylabel("SSE")
                plt.legend()
                fig.add_subplot(132)
                plt.plot(range(2, clusters), ss, 'b-', label='Silhouette Score')
                plt.scatter(n_clusters, ss[n_clusters - 2], s=250, c='r')
                plt.grid(True)
                plt.axvline(n_clusters, linestyle="--")
                plt.title('SS by Cluster Count')
                plt.xlabel("Number of cluster")
                plt.ylabel("Silhouette Score")
                plt.legend()

                fig.add_subplot(133)
                plt.plot(optimalK.gap_df.n_clusters, optimalK.gap_df.gap_value, linewidth=2)
                plt.scatter(optimalK.gap_df[optimalK.gap_df.n_clusters == n_clusters].n_clusters,
                            optimalK.gap_df[optimalK.gap_df.n_clusters == n_clusters].gap_value, s=250, c='r')
                plt.grid(True)
                plt.xlabel('Cluster Count')
                plt.ylabel('Gap Value')
                plt.title('Gap Values by Cluster Count')
                plt.axvline(n_clusters, linestyle="--")
                plt.show()

    def KMeans_clustering_func(self, X, k):
        """
        K Means Clustering function, which uses the K Means model from sklearn.

        These user-defined functions *must* take the X (input features) and a k
        when initializing OptimalK
        """
        # Include any clustering Algorithm that can return cluster centers

        m = KMeans(random_state=11, n_clusters=k)
        m.fit(X)

        # Return the location of each cluster center,
        # and the labels for each point.
        return m.cluster_centers_, m.predict(X)

    def guete_function(self):
        """
        This function calculates the Gütefunktion from the ML-Modell
        """
        # For ech Type
        for type in self.helperData.data['type'].unique():
            # Choose a specific Backend
            if type.path == '/tienda1/miembros/editar.jsp' and type.method == 'GET' and type.has_query==True and type.has_body==False:
                # Get Features from Dataframe
                X = self.helperData.data.loc[self.helperData.data['type'] == type]['features']
                # Parse Features to DataFrame
                X = pd.DataFrame(dict(X).values())
                # Normalize the Data
                scaler = StandardScaler()
                scaler.fit(X)
                X = scaler.transform(X)
                # Get the Labels
                cluster_labels = self.helperData.data.loc[self.helperData.data['type'] == type]['label']
                cluster_labels = cluster_labels.copy()

                # Remove specific Number of Labels
                modify_percentage = 0.6
                num_of_loops = len(cluster_labels) * modify_percentage

                while num_of_loops > 0:
                    random_index = random.randint(0, len(cluster_labels) - 1)

                    cluster_labels.iloc[random_index] = 2
                    num_of_loops = num_of_loops - 1

                clusters = 15
                d = {'label': cluster_labels}
                for n_clusters in range(2, clusters):
                    # iterating through cluster sizes
                    clusterer = KMeans(n_clusters=n_clusters, init='random', n_init=10, max_iter=300, tol=1e-04,
                                       random_state=0)
                    cluster_labels = clusterer.fit_predict(X)
                    d['n_cluster_' + str(n_clusters)] = cluster_labels

                df = pd.DataFrame(d)
                local_guete = []
                guete = []
                for n_clusters in range(2, clusters):
                    print("Clusters " + str(n_clusters))
                    for i in range(n_clusters):
                        attackLabel = len(df.loc[(df['n_cluster_' + str(n_clusters)] == i) & (df['label'] == 1)])
                        noAttackLabel = len(df.loc[(df['n_cluster_' + str(n_clusters)] == i) & (df['label'] == 0)])
                        num_of_datapoints = len(df.loc[(df['n_cluster_' + str(n_clusters)] == i)])
                        local_guete.append(abs(attackLabel - noAttackLabel) / num_of_datapoints)

                    guete.append(sum(local_guete) / len(local_guete))
                    local_guete = []

                plt.figure(figsize=(7, 7))
                n_clusters = 6
                plt.plot(range(2, clusters), guete, 'b-', label='Güte-Funktion')
                plt.scatter(n_clusters,
                            guete[n_clusters - 2], s=250, c='r')
                plt.grid(True)
                plt.axvline(n_clusters, linestyle="--")
                plt.title('Güte-Funktion by Cluster Count')
                plt.xlabel("Number of cluster")
                plt.ylabel("Güte-Funktion")
                plt.legend()
                plt.show()

    def score_cluster(self, true=None):
        # For ech Type
        for type in self.helperData.data['type'].unique():
            # Choose a specific Backend
            if type.path == '/tienda1/miembros/editar.jsp' and type.method == 'GET' and type.has_query==True and type.has_body==False:
                # Get Features from Dataframe
                X = self.helperData.data.loc[self.helperData.data['type'] == type]['features']
                # Parse Features to DataFrame
                X = pd.DataFrame(dict(X).values())
                # Normalize the Data
                scaler = StandardScaler()
                scaler.fit(X)
                X = scaler.transform(X)
                # Get the Labels
                global_cluster_labels = self.helperData.data.loc[self.helperData.data['type'] == type]['label']
                clusters = 15
                d = {'label': global_cluster_labels}
                TN = []
                TP = []
                FN = []
                FP = []
                for n_clusters in range(2, clusters):
                    # iterating through cluster sizes
                    clusterer = KMeans(n_clusters=n_clusters, init='random', n_init=10, max_iter=300, tol=1e-04,
                                       random_state=0)
                    cluster_labels_predicted = clusterer.fit_predict(X)
                    # Predict for the test set
                    df_training_data = pd.DataFrame()
                    df_training_data = df_training_data.assign(predicted_cluster=clusterer.predict(X))
                    df_training_data = df_training_data.assign(labels=global_cluster_labels)
                    clusters = []
                    for i in range(n_clusters):
                        clusters.append([
                            df_training_data[
                                (df_training_data.labels < 1) & (df_training_data.predicted_cluster == i)].shape[0],
                            df_training_data[
                                (df_training_data.labels > 0) & (df_training_data.predicted_cluster == i)].shape[0]])

                    self.alert_clusters = []
                    for i in range(n_clusters):
                        if clusters[i][0] < clusters[i][1]:
                            self.alert_clusters.append(i)
                    cluster_labels_predicted = cluster_labels_predicted.tolist()
                    for l in range(0, len(cluster_labels_predicted)):
                        if cluster_labels_predicted[l] in self.alert_clusters:
                            cluster_labels_predicted[l] = 1
                        else:
                            cluster_labels_predicted[l] = 0

                    d['n_cluster_' + str(n_clusters)] = cluster_labels_predicted
                    print(global_cluster_labels.to_numpy())
                    print(np.array(cluster_labels_predicted))
                    tn, fp, fn, tp = metrics.confusion_matrix(global_cluster_labels.to_numpy(), np.array(cluster_labels_predicted),normalize='all').ravel()
                    TN.append(tn)
                    FP.append(fp)
                    FN.append(fn)
                    TP.append(tp)

                df = pd.DataFrame(d)

                fig, axs = plt.subplots(2,2,figsize=(10, 10))
                n_clusters = 15
                axs[0,0].plot(range(2, n_clusters), np.array(TP), 'b-')
                axs[0,0].grid(True)
                axs[0,0].set_title('True Positive')
                axs[0,0].set_xlabel("Number of cluster")
                axs[0,0].set_ylabel("True Positive in %")
                axs[0,1].plot(range(2, n_clusters), np.array(FP), 'b-')
                axs[0,1].grid(True)
                axs[0,1].set_title('False Positive')
                axs[0,1].set_xlabel("Number of cluster")
                axs[0,1].set_ylabel("False Positive in %")
                axs[1,0].plot(range(2, n_clusters), np.array(FN), 'b-')
                axs[1,0].grid(True)
                axs[1,0].set_title('False Negative')
                axs[1,0].set_xlabel("Number of cluster")
                axs[1,0].set_ylabel("False Negative in %")
                axs[1,1].plot(range(2, n_clusters), np.array(TN), 'b-')
                axs[1,1].grid(True)
                axs[1,1].set_title('True Negative')
                axs[1,1].set_xlabel("Number of cluster")
                axs[1,1].set_ylabel("True Negative in %")
                plt.show()


helperData = HelperDataClass()
#helperData.count_labels_per_type()
logRegressionAnalytics = HelperLogRegressionPerfAnalytics(helperData)
logRegressionAnalytics.evaluate_log_Regression()
logRegressionAnalytics.get_conf_matrix()
logRegressionAnalytics.get_distance_distribution()
kMeansAnalytics = HelperKMeansPerfAnalytics(helperData)
kMeansAnalytics.score_cluster()
kMeansAnalytics.eval_num_of_cluster()
kMeansAnalytics.guete_function()

# %%
