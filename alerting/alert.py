from dataclasses import dataclass
from alerting.IObservable import IObservable
from alerting.IObserver import IObserver


@dataclass
class Alert:
    msg: str
    

class Alerting(IObserver):
    def update(self, observable: IObservable, alert: Alert) -> None:
        print(f"ALERT: {alert.msg}")
