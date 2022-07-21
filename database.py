import ZODB, ZODB.FileStorage
import transaction
import copy
import threading, queue

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
    write_object(name, obj)
        Writes an object to the database under a specific namespace.
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
        if not self.if_exists("body_ngrams"):
            self.write_object("body_ngrams", {})
        if not self.if_exists("query_ngrams"):
            self.write_object("query_ngrams", {})
        if not self.if_exists("data"):
            self.write_object("data", [])


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

        item = (name, obj)
        self.queue.put(item)


    def if_exists(self, name):
        """
        Checks if the namespace exists in the database.

        Parameters
        ----------
        name : str
            The namespace that has to be checked.
        
        Returns
        ----------
        bool
            Boolean if it exists or not.
        """

        connection = self.db.open()
        root = connection.root()
        res = name in root
        connection.close()
        return res


    def print_root(self):
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
                connection = self.db.open()
                root = connection.root()
                root[name] = copy.deepcopy(obj)
                transaction.commit()
                connection.close()
                self.queue.task_done()
