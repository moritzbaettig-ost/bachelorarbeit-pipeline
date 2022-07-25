from abc import ABC, abstractmethod
import ZODB, ZODB.FileStorage
import transaction
import copy
import threading, queue
from BTrees.OOBTree import BTree
from datetime import datetime
from type import Type
import persistent.list


class DatabaseHandlerStrategy(ABC):
    @abstractmethod
    def write(self, name: str, data: object) -> None:
        pass

    
    @abstractmethod
    def read(self, name: str) -> object:
        pass


    @abstractmethod
    def _write_worker(self) -> None:
        pass


class DefaultStrategy(DatabaseHandlerStrategy):
    def __init__(self) -> None:
        self.queue = queue.Queue()
        self.maintenance_mode = False
        threading.Thread(target=self._write_worker, daemon=True).start()


    def write(self, name: str, data: object) -> None:
        item = (name, data)
        self.queue.put(item)


    def read(self, name: str) -> object:
        connection = self.db.open()
        root = connection.root()
        # Check if object exists in root namespace
        if name in root:
            # Copy the object from the database
            obj = copy.deepcopy(root[name])
        else:
            # Return False if the object does not exist in the database
            obj = False
        connection.close()
        return obj


    def _write_worker(self) -> None:
        while True:
            if not self.maintenance_mode:
                item = self.queue.get()
                name = item[0]
                obj = item[1]
                connection = self.db.open()
                root = connection.root()
                root[name] = copy.deepcopy(obj)
                transaction.commit()
                connection.close()
                self.queue.task_done()


class DatabaseHandler:
    """
    This class is used to handle all the database connections from the application to the ZODB and therefore prevent locking problems.

    Attributes
    ----------
    db : DB
        The database object that represents the ZODB.
    queue: Queue
        The queue that handles the writes for the DB with de FIFO principle.
    maintenance_mode: bool
        If true, the queue is interrupted and waits until the maintenance is over.

    Methods
    ----------
    get_object(name)
        Reads an object from the database that is stored under a specific namespace and returns it.
    get_data()
        Returns the ML training data from the databse.
    get_query_ngrams(type)
        Returns the query ngram pool of a specific type.
    get_body_ngrams(type)
        Returns the body ngram pool of a specific type.
    write_object(name, obj)
        Writes an object to the database under a specific namespace.
    write_data(obj)
        Appends a new dataset for the ML training to the database.
    write_query_ngrams(type, ngrams)
        Appends a set of newly calculated query ngrams to the databse.
    write_body_ngrams(type, ngrams)
        Appends a set of newly calculated body ngrams to the databse.
    if_exists(name)
        Checks if the namespace exists in the database.
    print_root()
        Prints the contents of the database tree.
    _write_worker()
        Defines the worker function for the DB write daemon thread.
    """

    def __init__(self):
        storage = ZODB.FileStorage.FileStorage('db.fs')
        self.db = ZODB.DB(storage)
        self._strategy = DefaultStrategy()


    def set_strategy(self, strategy: DatabaseHandlerStrategy) -> None:
        self._strategy = strategy


    def read(self, name: str) -> object:
        """
        Reads an object from the database that is stored under a specific namespace and returns it.

        Parameters
        ----------
        name: str
            The namespace under that the object is stored.
        
        Returns
        ----------
        object
            The object.
        """

        return self._strategy.read(name)


    # TODO: Move in Model Strategy
    def get_data(self) -> dict:
        """
        Returns the ML training data from the databse.

        Returns
        ----------
        dict
            The dictionary with the training data.
        """

        connection = self.db.open()
        root = connection.root()
        res = dict(root["data"])
        connection.close()
        return res


    def write_object(self, name: str, data: object) -> None:
        """
        Writes an object to the database under a specific namespace.     
        Parameters
        ----------
        name : str
            The namespace under that the object should be stored.
        obj : object
            The object that has to be stored.
        """

        self._strategy.write(name, data)


    # TODO: Move in Model Strategy
    def write_data(self, obj: dict) -> None:
        """
        Appends a new dataset for the ML training to the database.

        Parameters
        ----------
        obj: dict
            The dictionary with the new feature data.
        """

        item = ("data", obj, None)
        self.queue.put(item)


    def print_root(self) -> None:
        """
        Prints the contents of the database tree.
        """
        
        connection = self.db.open()
        root = connection.root()
        print(root.items())
        connection.close()


    #TODO
    def _write_worker(self) -> None:
        """
        Defines the worker function for the DB write daemon thread.
        """

        while True:
            if not self.maintenance_mode:
                item = self.queue.get()
                name = item[0]
                obj = item[1]
                type = item[2]
                connection = self.db.open()
                root = connection.root()
                if name == "data":
                    root["data"].insert(datetime.now(), obj)
                elif name == "query_ngrams":
                    (root["query_ngrams"].get(type))["monograms"].append(obj["monograms"])
                    (root["query_ngrams"].get(type))["bigrams"].append(obj["bigrams"])
                    (root["query_ngrams"].get(type))["hexagrams"].append(obj["hexagrams"])
                elif name == "body_ngrams":
                    (root["body_ngrams"].get(type))["monograms"].append(obj["monograms"])
                    (root["body_ngrams"].get(type))["bigrams"].append(obj["bigrams"])
                    (root["body_ngrams"].get(type))["hexagrams"].append(obj["hexagrams"])
                else:
                    root[name] = copy.deepcopy(obj)
                transaction.commit()
                connection.close()
                self.queue.task_done()
