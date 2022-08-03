from re import S
from alerting.IObservable import IObservable
from alerting.IObserver import IObserver
from database import DatabaseHandler
from stages import Stage
from dtos import DTO, ExtractionModelDTO
from alerting.alert import Alert
import sys
import os
import importlib
import inspect


class ModelPluginInterface:
    """
    This Class defines the default methods which must be implemented in a Model Plugin

    Methods
    ----------
    train_model(training_data, training_labels)
        This method trains the ML-Model with the given input data
    predict(predicting_data)
        This method makes a prediction with the pretrained ML-Model for the given input vector
    """

    def train_model(self, training_data: list, training_labels: list) -> None:
        """
        This method trains an ML-Model with the given input data

        Parameters
        ----------
        training_data: list
            Is a list of dict objects fom all available reference data
        training_labels: list
            Is a list of all labels corresponding to the training_data list
        """
        pass

    def predict(self, predicting_data: list) -> list:
        """
        This method predicts if a feature vector refers to an attack or not

        Parameters
        ----------
        predicting_data: list
            Is the feature vector which needs to be predicted as attack or not

        Returns
        ----------
        list
            Returns a list of the pattern [attack (1)/no attack(0), probability of the attack]
        """
        pass


class Model(Stage, IObservable):
    """
    A class that represents the last stage of the ML-IDS pipeline.
    This class gets the computed feature vector from the extraction stage and classifies the request as attack or not.

    Attributes
    ----------
    successor: Stage
        The stage that follows this stage in the pipeline.
    plugins: list
        Is a list of all available plugins from the type ModelPluginInterface
    db_handler: DatabaseHandler
        This variable contains the connection to the database handling class
    mode: str
        This string contains if the pipeline is started in training or test mode
    _observers: list
        List of observers which is used for the alerting

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
            This string contains if the pipeline is started in training or test mode
        db_handler: DatabaseHandler
            This variable contains the connection to the database handling class
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

        # Set the Factory dict in the Plugin
        for plugin in self.plugins:
            plugin.set_model(self.db_handler)

    def run(self, dto: DTO) -> None:
        """
        This method is called when a new request is processed by the pipeline

        Parameters
        ----------
        dto: DTO
            The data transfer object to transport data between the extraction and the model stage.
        """

        # Check if the correct dto was passed to the model stage
        if not isinstance(dto, ExtractionModelDTO):
            sys.exit("Model: ExtractionModelDTO required.")
        # MODEL STAGE
        for plugin in self.plugins:
            # If the Pipeline is started in the training mode, the ML-Model must be actualised
            if self.mode == 'train':
                plugin.train_model(dto.type, self.db_handler)
            # print("Prediction")
            # Get the result from the ml-model
            ml_model_result = plugin.predict(dto.type, dto.features)
            # print(ml_model_result)
            # Check if the model predicts an attack
            if ml_model_result[0] > 0:
                # print("Attack")
                # Create an Alert
                alert = Alert(msg=f"Attack detected with accuracy({ml_model_result[1]})", source=f"Model Stage Plugin {(inspect.getfile(plugin.__class__)).split('/')[-1]}")
                self.notify(alert)
                return
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