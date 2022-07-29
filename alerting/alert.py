from dataclasses import dataclass
from alerting.IObservable import IObservable
from alerting.IObserver import IObserver
import io


@dataclass
class Alert:
    """
    A dataclass used to represent an Alert.
    
    Attributes
    ----------
    msg : str
        A string to print out the reason or the type of the Alert
    source: str
        The description of the source that created the Alert
    """

    msg: str
    source: str
    

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
        The alert gets logged in a file.

        Parameters
        ----------
        observable : IObservable
            The Observable that called the Observer.
        alert : Alert
            The Alert to be printed.
        """
        
        print(f"ALERT: {alert.msg}. Source: {alert.source}")
        f = open("alerting/log.txt", "a", encoding="utf-8")
        f.write(f"ALERT: {alert.msg}. Source: {alert.source}")
        f.write("\n")
        f.close()
