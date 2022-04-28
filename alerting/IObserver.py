from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from alerting.IObservable import IObservable
    from alerting.alert import Alert


class IObserver(ABC):
    """
    The observer interface declares the update method, used by observables.
    """
    
    @abstractmethod
    def update(self, observable: 'IObservable', alert: 'Alert') -> None:
        """
        Receive alert from observable
        """
        pass
