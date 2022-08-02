import pathlib
import sys

directory = pathlib.Path(__file__)
sys.path.append(directory.parent.parent.__str__())

from alerting.alert import Alerting, Alert
from alerting.IObservable import IObservable
from alerting.IObserver import IObserver

class TestObservable(IObservable):
    def __init__(self):
        self._observers = []


    def attach(self, observer: IObserver) -> None:
        self._observers.append(observer)


    def detach(self, observer: IObserver) -> None:
        self._observers.remove(observer)


    def notify(self, alert: Alert) -> None:        
        for observer in self._observers:
            observer.update(self, alert)

o = TestObservable()
a = Alerting(True)
o.attach(a)
for i in range(20):
    o.notify(Alert(f"test message {i}", "test source"))
    
