from abc import ABC, abstractmethod
import ZODB, ZODB.FileStorage, ZODB.DB
import transaction
import copy
import threading, queue
from BTrees.OOBTree import BTree
from datetime import datetime
from type import Type


class DatabaseHandlerStrategy(ABC):
    @abstractmethod
    def __init__(self, db: ZODB.DB, queue: queue.Queue) -> None:
        pass


    @abstractmethod
    def write(self, data: object, name: str, type: Type) -> None:
        pass

    
    @abstractmethod
    def read(self, name: str, type: Type) -> object:
        pass


    @abstractmethod
    def _write_worker(self, item: dict) -> None:
        pass


class DefaultStrategy(DatabaseHandlerStrategy):
    def __init__(self, db: ZODB.DB, queue: queue.Queue) -> None:
        self.db = db
        self.queue = queue


    def write(self, data: object, name: str, type: Type) -> None:
        item = {
            "worker_method": self._write_worker,
            "name": name,
            "object": data
        }
        self.queue.put(item)


    def read(self, name: str, type: Type) -> object:
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


    def _write_worker(self, item: dict) -> None:
        connection = self.db.open()
        root = connection.root()
        root[item["name"]] = copy.deepcopy(item["object"])
        transaction.commit()
        connection.close()


class DataStrategy(DatabaseHandlerStrategy):
    def __init__(self, db: ZODB.DB, queue: queue.Queue) -> None:
        self.db = db
        self.queue = queue
        connection = self.db.open()
        root = connection.root()
        if not "data" in root:
            root["data"] = BTree()
        transaction.commit()
        connection.close()


    def write(self, data: object, name: str, type: Type) -> None:
        item = {
            "worker_method": self._write_worker,
            "name": name,
            "object": data
        }
        self.queue.put(item)


    def read(self, name: str, type: Type) -> object:
        connection = self.db.open()
        root = connection.root()
        res = dict(root[name])
        connection.close()
        return res


    def _write_worker(self, item: dict) -> None:
        connection = self.db.open()
        root = connection.root()
        root[item["name"]].insert(datetime.now(), item["object"])
        transaction.commit()
        connection.close()


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

        self.queue = queue.Queue()
        self.maintenance_mode = False

        self.data_strategy = DataStrategy(self.db, self.queue)
        self._default_strategy = DefaultStrategy(self.db, self.queue)
        self._strategy = None

        threading.Thread(target=self._write_worker, daemon=True).start()


    def set_strategy(self, strategy: DatabaseHandlerStrategy) -> None:
        self._strategy = strategy


    def read(self, name: str, type: Type = None) -> object:
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

        if self._strategy is None:
            return self._default_strategy.read(name, type)
        else:
            return self._strategy.read(name, type)


    def write(self, data: object, name: str, type: Type = None) -> None:
        """
        Writes an object to the database under a specific namespace.     
        Parameters
        ----------
        name : str
            The namespace under that the object should be stored.
        obj : object
            The object that has to be stored.
        """

        if self._strategy is None:
            self._default_strategy.write(data, name, type)
        else:
            self._strategy.write(data, name, type)


    def print_root(self) -> None:
        """
        Prints the contents of the database tree.
        """
        
        connection = self.db.open()
        root = connection.root()
        print(root.items())
        connection.close()


    def _write_worker(self) -> None:
        """
        Defines the worker function for the DB write daemon thread.
        """

        while True:
            if not self.maintenance_mode:
                item = self.queue.get()
                item["worker_method"](item)
                self.queue.task_done()
