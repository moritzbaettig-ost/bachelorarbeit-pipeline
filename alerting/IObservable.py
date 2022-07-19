from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from alerting.IObserver import IObserver
    from alerting.alert import Alert


class IObservable(ABC):
    """
    The observable interface declares a set of methods for managing observers.

    Methods
    ----------
    attach(observer)
        Attaches an observer to the observable.
    detach(observer)
        Detaches an observer from the observable.
    notify(alert)
        Notify all observers about an alert.
    """

    @abstractmethod
    def attach(self, observer: 'IObserver') -> None:
        """
        Attaches an observer to the observable.

        Parameters
        ----------
        observer : IObserver
            The observer to attach.
        """

        pass

    @abstractmethod
    def detach(self, observer: 'IObserver') -> None:
        """
        Detaches an observer from the observable.

        Parameters
        ----------
        observer : IObserver
            The observer to detach.
        """

        pass

    @abstractmethod
    def notify(self, alert: 'Alert') -> None:
        """
        Notify all observers about an alert.

        Parameters
        ----------
        alert: Alert
            The alert being the reason for the notification.
        """

        pass
