from abc import ABC, abstractmethod
import ZODB, ZODB.FileStorage, ZODB.DB
import transaction
import copy
import threading, queue
from BTrees.OOBTree import BTree
from datetime import datetime
from type import Type


class DatabaseHandlerStrategy(ABC):
    """
    This interface defines the standard methods for all Strategies that implement database access logic for different components.

    Methods
    ----------
    write(data, name, type)
        Writes an object to the databse
    read(name, type)
        Reads an object from the database
    _write_worker(item)
        Defines the procedure of the daemon thread that works off the queue
    """

    @abstractmethod
    def __init__(self, db: ZODB.DB, queue: queue.Queue) -> None:
        """
        Parameters
        ----------
        db: ZODB.DB
            The reference to the DB object of the database handler
        queue: queue.Queue
            The reference to the queue object of the database handler
        """

        pass


    @abstractmethod
    def write(self, data: object, name: str, type: Type) -> None:
        """
        Writes an object to the databse

        Parameters
        ----------
        data: object
            The object that has to be written to the database
        name: str
            The namespace under which the object has to be saved or appended
        type: Type
            The type of the request
        """

        pass

    
    @abstractmethod
    def read(self, name: str, type: Type) -> object:
        """
        Reads an object from the database

        Parameters
        ----------
        name: str
            The namespace under which the object is saved
        type: Type
            The type of the request

        Returns
        ----------
        object
            The desired object
        """

        pass


    @abstractmethod
    def _write_worker(self, item: dict) -> None:
        """
        Defines the procedure of the daemon thread that works off the queue

        Parameters
        ----------
        item: dict
            The item with the write information that is passed to the queue
        """

        pass


class DefaultStrategy(DatabaseHandlerStrategy):
    """
    This class defines the default Strategy and implement default database access logic.

    Methods
    ----------
    write(data, name, type)
        Writes an object to the databse
    read(name, type)
        Reads an object from the database
    _write_worker(item)
        Defines the procedure of the daemon thread that works off the queue
    """

    def __init__(self, db: ZODB.DB, queue: queue.Queue) -> None:
        """
        Parameters
        ----------
        db: ZODB.DB
            The reference to the DB object of the database handler
        queue: queue.Queue
            The reference to the queue object of the database handler
        """

        self.db = db
        self.queue = queue


    def write(self, data: object, name: str, type: Type) -> None:
        """
        Writes an object to the databse

        Parameters
        ----------
        data: object
            The object that has to be written to the database
        name: str
            The namespace under which the object has to be saved or appended
        type: Type
            The type of the request
        """

        item = {
            "worker_method": self._write_worker,
            "name": name,
            "object": data
        }
        self.queue.put(item)


    def read(self, name: str, type: Type) -> object:
        """
        Reads an object from the database

        Parameters
        ----------
        name: str
            The namespace under which the object is saved
        type: Type
            The type of the request

        Returns
        ----------
        object
            The desired object
        """

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
        """
        Defines the procedure of the daemon thread that works off the queue

        Parameters
        ----------
        item: dict
            The item with the write information that is passed to the queue
        """

        connection = self.db.open()
        root = connection.root()
        root[item["name"]] = copy.deepcopy(item["object"])
        transaction.commit()
        connection.close()


class DataStrategy(DatabaseHandlerStrategy):
    """
    This class defines the Strategy that implements the database access logic for the machine learning training data.

    Methods
    ----------
    write(data, name, type)
        Writes an object to the databse
    read(name, type)
        Reads an object from the database
    _write_worker(item)
        Defines the procedure of the daemon thread that works off the queue
    """

    def __init__(self, db: ZODB.DB, queue: queue.Queue) -> None:
        """
        Parameters
        ----------
        db: ZODB.DB
            The reference to the DB object of the database handler
        queue: queue.Queue
            The reference to the queue object of the database handler
        """

        self.db = db
        self.queue = queue
        connection = self.db.open()
        root = connection.root()
        if not "data" in root:
            root["data"] = BTree()
        transaction.commit()
        connection.close()


    def write(self, data: object, name: str, type: Type) -> None:
        """
        Appends the BTree with a dataset

        Parameters
        ----------
        data: object
            The object that has to be written to the database
        name: str
            The namespace under which the object has to be saved or appended
        type: Type
            The type of the request (not used)
        """

        item = {
            "worker_method": self._write_worker,
            "name": name,
            "object": data
        }
        self.queue.put(item)


    def read(self, name: str, type: Type) -> object:
        """
        Reads the machine learning training data from the database

        Parameters
        ----------
        name: str
            The namespace under which the object is saved
        type: Type
            The type of the request (not used)

        Returns
        ----------
        object
            Machine Learning training data
        """

        connection = self.db.open()
        root = connection.root()
        res = dict(root[name])
        connection.close()
        return res


    def _write_worker(self, item: dict) -> None:
        """
        Defines the procedure of the daemon thread that works off the queue

        Parameters
        ----------
        item: dict
            The item with the write information that is passed to the queue
        """

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
    data_strategy: DataStrategy
        The Strategy that implements database access logic for the machine learning data
    _default_strategy: DefaultStrategy
        The default Strategy that implements the default database access logic
    _strategy: DatabaseHandlerStrategy
        The current Strategy

    Methods
    ----------
    set_strategy(strategy)
        Sets the current Strategy in which the database access logic is defined.
    read(name, type)
        Reads an object from the database that is stored under a specific namespace and returns it.
    write(data, name, type)
        Writes an object to the database under a specific namespace.
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
        """
        Sets the current Strategy in which the database access logic is defined.

        Parameters
        ----------
        strategy: DatabaseHandlerStrategy
            The new Strategy that has to be set
        """

        self._strategy = strategy


    def read(self, name: str, type: Type = None) -> object:
        """
        Reads an object from the database that is stored under a specific namespace and returns it.
        The database access logic from the current Strategy is used. If no Strategy is set, the default Strategy is used.

        Parameters
        ----------
        name: str
            The namespace under that the object is stored.
        type: Type
            The type of the request
        
        Returns
        ----------
        object
            The object read from the databse
        """

        if self._strategy is None:
            return self._default_strategy.read(name, type)
        else:
            return self._strategy.read(name, type)


    def write(self, data: object, name: str, type: Type = None) -> None:
        """
        Writes an object to the database under a specific namespace.     
        The database access logic from the current Strategy is used. If no Strategy is set, the default Strategy is used.

        Parameters
        ----------
        data: object
            The object that has to be stored.
        name : str
            The namespace under that the object should be stored.
        type: Type
            The type of the request
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
                self.db.pack()
                self.queue.task_done()
