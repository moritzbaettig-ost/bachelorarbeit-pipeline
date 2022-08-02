from dataclasses import dataclass
import logging
from logging.handlers import QueueHandler, QueueListener
from alerting.IObservable import IObservable
from alerting.IObserver import IObserver
import queue
import time


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

    Attributes
    ----------
    logging_mode: bool
        States if logging is activated or not
    logger: Logger
        The logger instance that is responsible for the logging
    
    Methods
    ----------
    update(observable, alert)
        Gets called by an Observable and prints an Alert with a specific message
    """
    
    def __init__(self, logging_mode: bool) -> None:
        """
        Parameters
        ----------
        logging_mode: bool
            States if logging is activated or not
        """

        self.logging_mode = logging_mode

        logging.basicConfig(filemode='a', datefmt='%H:%M:%S', level=logging.INFO)
        self.logger = logging.getLogger("Alerting")

        log_queue = queue.Queue()
        queue_handler = QueueHandler(log_queue)
        self.logger.addHandler(queue_handler)

        formatter = logging.Formatter('%(asctime)s, %(name)s %(levelname)s %(message)s')

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)

        file_handler = logging.FileHandler("alerting/log.log")
        file_handler.setFormatter(formatter)

        listener = QueueListener(log_queue, console_handler, file_handler)
        listener.start()

    
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
        
        log_string = f"ALERT: {alert.msg}. Source: {alert.source}"
        if self.logging_mode:
            self.logger.warning(log_string)
            # Workaround logging bug
            time.sleep(0.00000000001)
