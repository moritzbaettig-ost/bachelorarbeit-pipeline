import importlib
import sys
import os
from typing import List
from alerting.IObservable import IObservable
from alerting.IObserver import IObserver
from alerting.alert import Alert
from dtos.DTOs import DTO, AcquisitionFilterDTO, FilterTypingDTO
from message import IDSHTTPMessage
from stages import Stage


class FilterPluginInterface:
    def filter_request(self, message: IDSHTTPMessage) -> tuple[bool, str]:
        pass


class RequestFilter(Stage, IObservable):
    def __init__(self, successor: 'Stage'):
        if len(os.listdir('./stages/filter/plugins')) == 0:
            sys.exit("No filter plugin detcted. Please place default filter plugin in the filter plugis directory.")
        sys.path.append('./stages/filter/plugins')
        self.plugins = [
            importlib.import_module(f.split('.')[0], '.').Plugin()
            for f in next(os.walk('stages/filter/plugins'))[2]
        ]
        super().__init__(successor)

    def run(self, dto: DTO) -> None:
        if not isinstance(dto, AcquisitionFilterDTO):
            sys.exit("Filter: AcquisitionFilterDTO required.")
        for plugin in self.plugins:
            filter_response = plugin.filter_request(dto.message)
            if filter_response[0]:
                alert = Alert(msg=filter_response[1])
                self.notify(alert)
                return
        new_dto = FilterTypingDTO(message=dto.message)
        self.successor.run(new_dto)

    _observers: List[IObserver] = []

    def attach(self, observer: IObserver) -> None:
        self._observers.append(observer)

    def detach(self, observer: IObserver) -> None:
        self._observers.remove(observer)

    def notify(self, alert: Alert) -> None:
        for observer in self._observers:
            observer.update(self, alert)