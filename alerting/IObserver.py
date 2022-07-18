from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from alerting.IObservable import IObservable
    from alerting.alert import Alert


class IObserver(ABC):
    """
    The observer interface declares the update method, used by observables.

    Methods
    ----------
    update(observable, alert)
        Receives alert from observable.
    """
    
    @abstractmethod
    def update(self, observable: 'IObservable', alert: 'Alert') -> None:
        """
        Receives alert from observable.

        Parameters
        ----------
        observable : IObservable
            The observable from which the alert comes.
        alert : Alert
            The alert received from the observable.
        """
        
        pass
