from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from alerting.IObserver import IObserver
    from alerting.alert import Alert


class IObservable(ABC):
    """
    The observable interface declares a set of methods for managing observers.
    """

    @abstractmethod
    def attach(self, observer: 'IObserver') -> None:
        """
        Attach an observer to the observable.
        """
        pass

    @abstractmethod
    def detach(self, observer: 'IObserver') -> None:
        """
        Detach an observer from the observable.
        """
        pass

    @abstractmethod
    def notify(self, alert: 'Alert') -> None:
        """
        Notify all observers about an alert.
        """
        pass
