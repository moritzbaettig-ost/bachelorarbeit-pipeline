from alerting.IObservable import IObservable
from alerting.IObserver import IObserver
from database import DatabaseHandler
from stages import Stage
from dtos import DTO, ExtractionModelDTO
from alerting.alert import Alert
import sys
import os
import importlib


class ModelPluginInterface:
    """This Class defines the default methods which must be implemented in a Model Plugin"""

    def train_model(self, training_data: list, training_labels: list) -> None:
        pass

    def predict(self, predicting_data) -> list:
        pass


class Model(Stage, IObservable):
    def __init__(self, successor: 'Stage', mode: str, db_handler: DatabaseHandler):
        self.successor = successor
        if len(os.listdir('./stages/model/plugins')) == 0:
            sys.exit("No model plugin detected. Please place default model plugin in the model plugin directory.")
        sys.path.append('./stages/model/plugins')
        self.plugins = [
            importlib.import_module(f.split('.')[0], '.').Plugin()
            for f in next(os.walk('stages/model/plugins'))[2]
        ]
        self.db_handler = db_handler
        self.mode = mode
        self._observers = []

        # Set the Fabric in the Plugin
        for plugin in self.plugins:
            plugin.set_model(self.db_handler)

    def run(self, dto: DTO) -> None:
        if not isinstance(dto, ExtractionModelDTO):
            sys.exit("Model: ExtractionModelDTO required.")
        # MODEL STAGE
        for plugin in self.plugins:
            # If the Pipeline is started in the training mode, the ML-Model must be actualised
            if self.mode == 'train':
                plugin.train_model(dto.type, self.db_handler)
            print("Prediction")
            # Get the result from the ml-model
            ml_model_result = plugin.predict(dto.type, dto.features)
            print(ml_model_result)
            # Check if the model predicts an attack
            if ml_model_result[0] > 0:
                print("Attack")
                # Create an Alert
                alert = Alert(msg=f"Attack detected with accuracy({ml_model_result[1]})")
                self.notify(alert)
                return
            # define plugin iteration here
            pass

    def attach(self, observer: IObserver) -> None:
        self._observers.append(observer)

    def detach(self, observer: IObserver) -> None:
        self._observers.remove(observer)

    def notify(self, alert: Alert) -> None:
        for observer in self._observers:
            observer.update(self, alert)