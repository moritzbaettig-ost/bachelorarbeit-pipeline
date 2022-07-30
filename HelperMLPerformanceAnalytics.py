import copy
import warnings

import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import silhouette_score
from sklearn.model_selection import learning_curve
from sklearn.model_selection import ShuffleSplit
import ZODB, ZODB.FileStorage, ZODB.DB
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from gap_statistic import OptimalK



class HelperDataClass:
    def __init__(self):
        storage = ZODB.FileStorage.FileStorage('db.fs')
        self.db = ZODB.DB(storage)
        connection = self.db.open()
        root = connection.root()
        self.data = pd.DataFrame()
        # Check if object exists in root namespace
        if "data" in root:
            # Copy the object from the database
            obj = copy.deepcopy(root["data"])
            self.data = pd.DataFrame(dict(obj).values())
        else:
            # Return False if the object does not exist in the database
            obj = False
        connection.close()


class HelperLogRegressionPerfAnalytics:
    def __init__(self):
        self.helperData = HelperDataClass()

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

        axes : array-like of shape (3,), default=None
            Axes to use for plotting the curves.

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
            _, axes = plt.subplots(1, 3, figsize=(20, 5))

        axes[0].set_title(title)
        if ylim is not None:
            axes[0].set_ylim(*ylim)
        axes[0].set_xlabel("Training examples")
        axes[0].set_ylabel("Score")

        train_sizes, train_scores, test_scores, fit_times, _ = learning_curve(estimator,X,y,cv=cv,n_jobs=n_jobs,train_sizes=train_sizes,return_times=True)
        train_scores_mean = np.mean(train_scores, axis=1)
        train_scores_std = np.std(train_scores, axis=1)
        test_scores_mean = np.mean(test_scores, axis=1)
        test_scores_std = np.std(test_scores, axis=1)
        fit_times_mean = np.mean(fit_times, axis=1)
        fit_times_std = np.std(fit_times, axis=1)

        # Plot learning curve
        axes[0].grid()
        axes[0].fill_between(
            train_sizes,
            train_scores_mean - train_scores_std,
            train_scores_mean + train_scores_std,
            alpha=0.1,
            color="r",
        )
        axes[0].fill_between(
            train_sizes,
            test_scores_mean - test_scores_std,
            test_scores_mean + test_scores_std,
            alpha=0.1,
            color="g",
        )
        axes[0].plot(
            train_sizes, train_scores_mean, "o-", color="r", label="Training score"
        )
        axes[0].plot(
            train_sizes, test_scores_mean, "o-", color="g", label="Cross-validation score"
        )
        axes[0].legend(loc="best")

        # Plot n_samples vs fit_times
        axes[1].grid()
        axes[1].plot(train_sizes, fit_times_mean, "o-")
        axes[1].fill_between(
            train_sizes,
            fit_times_mean - fit_times_std,
            fit_times_mean + fit_times_std,
            alpha=0.1,
        )
        axes[1].set_xlabel("Training examples")
        axes[1].set_ylabel("fit_times")
        axes[1].set_title("Scalability of the model")

        # Plot fit_time vs score
        fit_time_argsort = fit_times_mean.argsort()
        fit_time_sorted = fit_times_mean[fit_time_argsort]
        test_scores_mean_sorted = test_scores_mean[fit_time_argsort]
        test_scores_std_sorted = test_scores_std[fit_time_argsort]
        axes[2].grid()
        axes[2].plot(fit_time_sorted, test_scores_mean_sorted, "o-")
        axes[2].fill_between(
            fit_time_sorted,
            test_scores_mean_sorted - test_scores_std_sorted,
            test_scores_mean_sorted + test_scores_std_sorted,
            alpha=0.1,
        )
        axes[2].set_xlabel("fit_times")
        axes[2].set_ylabel("Score")
        axes[2].set_title("Performance of the model")

        return plt

        # Plot
    def evaluate_log_Regression(self):
        num_of_plots = len(self.helperData.data['type'].unique())
        fig, axes = plt.subplots(3, num_of_plots, figsize=(5*num_of_plots, 15))
        i=0
        for type in self.helperData.data['type'].unique():
            X = self.helperData.data.loc[self.helperData.data['type'] == type]['features']
            y = self.helperData.data.loc[self.helperData.data['type'] == type]['label']
            title = "Learning Curves\n" + type.path
            # Cross validation with 50 iterations to get smoother mean test and train
            # score curves, each time with 20% data randomly selected as a validation set.
            cv = ShuffleSplit(n_splits=50, test_size=0.2, random_state=0)
            estimator = Pipeline([('scaler', StandardScaler()), ('lr', LogisticRegression(random_state=0))])
            features = pd.DataFrame(dict(X).values())
            self.plot_learning_curve(estimator, title, features, y, axes=axes[:, i], ylim=(0.7, 1.01), cv=cv, n_jobs=4)
            i = i +1
        plt.show()

class HelperKMeansPerfAnalytics:
    def __init__(self):
        self.helperData = HelperDataClass()

    def eval_num_of_cluster(self):
        for type in self.helperData.data['type'].unique():
            if type.path == '/vulnbank/online/api.php':
                X = self.helperData.data.loc[self.helperData.data['type'] == type]['features']
                X = pd.DataFrame(dict(X).values())
                scaler = StandardScaler()
                scaler.fit(X)
                X = scaler.transform(X)
                cluster_labels = self.helperData.data.loc[self.helperData.data['type'] == type]['label']
                clusters = 15
                elbow = []
                ss = []
                for n_clusters in range(2,clusters):
                    print(n_clusters)
                    # iterating through cluster sizes
                    clusterer = KMeans(n_clusters=n_clusters, init='random', n_init=10, max_iter=300, tol=1e-04, random_state=0)
                    cluster_labels = clusterer.fit_predict(X)
                    # Finding the average silhouette score
                    silhouette_avg = silhouette_score(X, cluster_labels)
                    ss.append(silhouette_avg)
                    print("For n_clusters =", n_clusters, "The average silhouette_score is :", silhouette_avg)
                    # Finding the average SSE"
                    elbow.append(clusterer.inertia_)  # Inertia: Sum of distances of samples to their closest cluster center

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
                           elbow[n_clusters-2], s=250, c='r')
                plt.grid(True)
                plt.axvline(n_clusters, linestyle="--")
                plt.title('SSE by Cluster Count')
                plt.xlabel("Number of cluster")
                plt.ylabel("SSE")
                plt.legend()
                fig.add_subplot(132)
                plt.plot(range(2, clusters), ss, 'b-', label='Silhouette Score')
                plt.scatter(n_clusters, ss[n_clusters-2], s=250, c='r')
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

#logRegressionAnalytics = HelperLogRegressionPerfAnalytics()
#logRegressionAnalytics.evaluate_log_Regression()
kMeansAnalytics = HelperKMeansPerfAnalytics()
kMeansAnalytics.eval_num_of_cluster()
