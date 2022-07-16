from alerting.IObservable import IObservable
from alerting.IObserver import IObserver
from stages import Stage
from dtos import DTO, ExtractionModelDTO
from alerting.alert import Alert
import sys
import os
import importlib

class ModelPluginInterface:
    # Define functions here
    pass

class Model(Stage, IObservable):
    def __init__(self, successor: 'Stage'):
        if len(os.listdir('./stages/model/plugins')) == 0:
            sys.exit("No model plugin detected. Please place default model plugin in the model plugin directory.")
        sys.path.append('./stages/model/plugins')
        self.plugins = [
            importlib.import_module(f.split('.')[0], '.').Plugin()
            for f in next(os.walk('stages/model/plugins'))[2]
        ]
        self._observers = []
        super().__init__(successor)

    def run(self, dto: DTO) -> None:
        if not isinstance(dto, ExtractionModelDTO):
            sys.exit("Model: ExtractionModelDTO required.")
        # MODEL STAGE
        for plugin in self.plugins:
            # define plugin iteration here
            pass

    def attach(self, observer: IObserver) -> None:
        self._observers.append(observer)

    def detach(self, observer: IObserver) -> None:
        self._observers.remove(observer)

    def notify(self, alert: Alert) -> None:
        for observer in self._observers:
            observer.update(self, alert)