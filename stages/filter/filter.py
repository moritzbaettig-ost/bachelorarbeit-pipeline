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
    """
    This class defines the default method that must be implemented in all filter plugins.

    Methods
    ----------
    filter_request(message)
        Returns if the given message should be filtered or not.
    """

    def filter_request(self, message: IDSHTTPMessage) -> tuple[bool, str]:
        """
        Returns if the given message should be filtered or not.

        Parameters
        ----------
        message: IDSHTTPMessage
            The HTTP message that should be filtered or not.

        Returns
        ----------
        tuple[bool, str]
            If the message should be filtered and the reason for it.
        """

        pass


class RequestFilter(Stage, IObservable):
    """
    This class represents the second stage of the ML-IDS pipeline.
    This stage decides if an HTTP request should be filtered or not.

    Attributes
    ----------
    successor: Stage
        The stage that follows this stage in the pipeline.
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

    def __init__(self, successor: 'Stage'):
        """
        Parameters
        ----------
        successor: Stage
            The stage that follows this stage in the pipeline.
        """

        self.successor = successor
        if len(os.listdir('./stages/filter/plugins')) == 0:
            sys.exit("No filter plugin detcted. Please place default filter plugin in the filter plugis directory.")
        sys.path.append('./stages/filter/plugins')
        self.plugins = [
            importlib.import_module(f.split('.')[0], '.').Plugin()
            for f in next(os.walk('stages/filter/plugins'))[2]
        ]
        self._observers = []


    def run(self, dto: DTO) -> None:
        """
        The method that gets called by the previous stage.

        Parameters
        ----------
        dto: DTO
            The data transfer object that is received from the previous stage.
        """

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
