from alerting.IObservable import IObservable
from alerting.IObserver import IObserver
from stages import Stage
from dtos import DTO, ExtractionModelDTO
from alerting.alert import Alert
import sys

class Model(Stage, IObservable):
    def __init__(self, successor: 'Stage'):
        self._observers = []
        super().__init__(successor)

    def run(self, dto: DTO) -> None:
        if not isinstance(dto, ExtractionModelDTO):
            sys.exit("Model: ExtractionModelDTO required.")
            # MODEL STAGE

    def attach(self, observer: IObserver) -> None:
        self._observers.append(observer)

    def detach(self, observer: IObserver) -> None:
        self._observers.remove(observer)

    def notify(self, alert: Alert) -> None:
        for observer in self._observers:
            observer.update(self, alert)