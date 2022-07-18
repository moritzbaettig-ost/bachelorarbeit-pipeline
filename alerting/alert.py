from dataclasses import dataclass
from alerting.IObservable import IObservable
from alerting.IObserver import IObserver


@dataclass
class Alert:
    """
    A dataclass used to represent an Alert.
    
    Attributes
    ----------
    msg : str
        A string to print out the reason or the type of the Alert
    """

    msg: str
    

class Alerting(IObserver):
    """
    A class that represents a concrete Observer and prints Alerts.
    
    Methods
    ----------
    update(observable, alert)
        Gets called by an Observable and prints an Alert with a specific message
    """

    def update(self, observable: IObservable, alert: Alert) -> None:
        """
        Gets called by an Observable and prints an Alert with a specific message.

        Parameters
        ----------
        observable : IObservable
            The Observable that called the Observer.
        alert : Alert
            The Alert to be printed.
        """
        
        print(f"ALERT: {alert.msg}")
