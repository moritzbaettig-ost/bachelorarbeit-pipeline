import ZODB, ZODB.FileStorage
import transaction
import copy

class Database():
    def __init__(self):
        storage = ZODB.FileStorage.FileStorage('db.fs')
        self.db = ZODB.DB(storage)
        self.wait = False
        if not self.if_exists("body_ngrams"):
            self.write_object("body_ngrams", {})
        if not self.if_exists("query_ngrams"):
            self.write_object("query_ngrams", {})
        if not self.if_exists("data"):
            self.write_object("data", [])

    def get_object(self, name):
        while self.wait:
            pass
        self.wait = True
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
        self.wait = False
        return obj

    def write_object(self, name, obj):
        while self.wait:
            pass
        self.wait = True
        connection = self.db.open()
        root = connection.root()
        root[name] = copy.deepcopy(obj)
        transaction.commit()
        connection.close()
        self.wait = False

    def if_exists(self, name):
        while self.wait:
            pass
        self.wait = True
        connection = self.db.open()
        root = connection.root()
        res = name in root
        connection.close()
        self.wait = False
        return res

    def print_root(self):
        while self.wait:
            pass
        self.wait = True
        connection = self.db.open()
        root = connection.root()
        print(root.items())
        connection.close()
        self.wait = False