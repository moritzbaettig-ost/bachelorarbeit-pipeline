from stages.model import ModelPluginInterface
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from type import Type


class Plugin(ModelPluginInterface):
    def __init__(self):
        self.model_dict = {}

    def get_model(self, type: Type):
        if type not in self.model_dict:
            self.model_dict[type] = LogisticRegression()

        return self.model_dict[type]

    def train_model(self, type: Type):
        self.get_model(type).train_model()

    def predict(self, type: Type, predicting_data: dict):
        self.get_model(type).predict(predicting_data)


class LogisticRegression:
    def __init__(self):
        self.model = False
        self.score = 0
        self.num

    def train_model(self, training_data: list, training_labels: list) -> None:
        x_train_set, x_test_set, y_train_labels, y_test_labels = train_test_split(training_data, training_labels,
                                                                                  test_size=0.2, random_state=22)
        clf = Pipeline([('scaler', StandardScaler()), ('lr', LogisticRegression(random_state=0))])
        clf.fit(x_train_set, y_train_labels)
        self.model = clf
        self.model.predict(x_test_set)
        self.score = clf.score(x_test_set, y_test_labels)

    def predict(self, predicting_data: dict):
        if not self.model:
            return 0
        else:
            return self.model.predict(predicting_data)
