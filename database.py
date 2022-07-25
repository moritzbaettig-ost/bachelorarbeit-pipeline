import ZODB, ZODB.FileStorage
import transaction
import copy
import threading, queue
from BTrees.OOBTree import BTree
from datetime import datetime
from type import Type
import persistent.list

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
        threading.Thread(target=self._write_worker, daemon=True).start()

        connection = self.db.open()
        root = connection.root()
        if not "body_ngrams" in root:
            root["body_ngrams"] = BTree()
        if not "query_ngrams" in root:
            root["query_ngrams"] = BTree()
        if not "data" in root:
            root["data"] = BTree()
        transaction.commit()
        connection.close()


    def get_object(self, name):
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


    def get_query_ngrams(self, type: Type) -> dict:
        """
        Returns the query ngram pool of a specific type.

        Parameters
        ----------
        type: Type
            The HTTP message type
        
        Returns
        ----------
        dict
            The dictionary with the query ngram pool
        """

        connection = self.db.open()
        root = connection.root()
        if not root["query_ngrams"].has_key(type):
            root["query_ngrams"].insert(type, {
                    "monograms": persistent.list.PersistentList(),
                    "bigrams": persistent.list.PersistentList(),
                    "hexagrams": persistent.list.PersistentList()
                })
            transaction.commit()
        res =  {
            "monograms": list(root["query_ngrams"][type]["monograms"]),
            "bigrams": list(root["query_ngrams"][type]["bigrams"]),
            "hexagrams": list(root["query_ngrams"][type]["hexagrams"])
        }
        connection.close()
        return res


    def get_body_ngrams(self, type: Type) -> dict:
        """
        Returns the body ngram pool of a specific type.

        Parameters
        ----------
        type: Type
            The HTTP message type
        
        Returns
        ----------
        dict
            The dictionary with the body ngram pool
        """

        connection = self.db.open()
        root = connection.root()
        if not root["body_ngrams"].has_key(type):
            root["body_ngrams"].insert(type, {
                    "monograms": persistent.list.PersistentList(),
                    "bigrams": persistent.list.PersistentList(),
                    "hexagrams": persistent.list.PersistentList()
                })
            transaction.commit()
        res =  {
            "monograms": list(root["body_ngrams"][type]["monograms"]),
            "bigrams": list(root["body_ngrams"][type]["bigrams"]),
            "hexagrams": list(root["body_ngrams"][type]["hexagrams"])
        }
        connection.close()
        return res


    def write_object(self, name, obj):
        """
        Writes an object to the database under a specific namespace.     
        Parameters
        ----------
        name : str
            The namespace under that the object should be stored.
        obj : object
            The object that has to be stored.
        """

        item = (name, obj, None)
        self.queue.put(item)


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


    def write_query_ngrams(self, type: Type, ngrams: dict) -> None:
        """
        Appends a set of newly calculated query ngrams to the databse.

        Parameters
        ----------
        type: Type
            The HTTP message type
        ngrams: dict
            The ngrams dictionary
        """

        item = ("query_ngrams", ngrams, type)
        self.queue.put(item)


    def write_body_ngrams(self, type: Type, ngrams: dict) -> None:
        """
        Appends a set of newly calculated body ngrams to the databse.

        Parameters
        ----------
        type: Type
            The HTTP message type
        ngrams: dict
            The ngrams dictionary
        """

        item = ("body_ngrams", ngrams, type)
        self.queue.put(item)


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
