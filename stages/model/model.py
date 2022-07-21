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
    """
    This class defines the default methods which must be implemented in a model plugin.

    Methods
    ----------
    train_model(training_data, training_labels)
        This method reads the required features from the database and trains the ML model.
    predict(predicting_data)
        This method predicts if the request is an attack.
    """


    def train_model(self, training_data: list, training_labels: list) -> None:
        """
        This method reads the required features from the database and trains the ML model.

        Parameters
        ----------
        training_data: list
            The data used to train the model.
        training_labels: list
            The labels used to train the supervised model.
        """

        pass


    def predict(self, predicting_data) -> list:
        """
        This method predicts if the request is an attack.

        Parameters
        ----------
        predicting_data
            The data used to predict if the request is an attack.
        """

        pass


class Model(Stage, IObservable):
    """
    A class that represents the fifth and last stage of the ML-IDS- pipeline.
    This stage creates and manages ML models used to predict if the request is an attack or not.

    Attributes
    ----------
    successor: Stage
        The stage that follows this stage in the pipeline.
    db_handler: DatabaseHandler
        The handler for the database connection.
    mode: str
        The mode of the pipeline ("train" or "test")
    observers: list[IObserver]
        The list of the registered observers.

    Methods
    ----------
    run(dto)
        The method that gets called by the previous stage.
    attach(observer)
        Attaches an observer to the observable.
    detach(observer)
        Detaches an observer from the observable.
    notify(alert)
        Notify all observers about an alert.
    """


    def __init__(self, successor: 'Stage', mode: str, db_handler: DatabaseHandler):
        """
        Parameters
        ----------
        successor: Stage
            The stage that follows this stage in the pipeline.
        mode: str
            The mode of the pipeline ("train" or "test")
        db_handler: DatabaseHandler
            The handler for the database connection.
        """

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
        """
        The method that gets called by the previous stage.

        Parameters
        ----------
        dto: DTO
            The data transfer object that is received from the previous stage.
        """

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
        """
        Attaches an observer to the observable.

        Parameters
        ----------
        observer : IObserver
            The observer to attach.
        """

        self._observers.append(observer)


    def detach(self, observer: IObserver) -> None:
        """
        Detaches an observer from the observable.

        Parameters
        ----------
        observer : IObserver
            The observer to detach.
        """

        self._observers.remove(observer)


    def notify(self, alert: Alert) -> None:
        """
        Notify all observers about an alert.

        Parameters
        ----------
        alert: Alert
            The alert being the reason for the notification.
        """
        
        for observer in self._observers:
            observer.update(self, alert)
