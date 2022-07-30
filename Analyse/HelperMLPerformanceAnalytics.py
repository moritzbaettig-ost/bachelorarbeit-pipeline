

class HelperDataClass:
    def __init__(self):
        # Hallo
        print("Hallo")
        connection = self.db.open()
        root = connection.root()
        print(root)
        # Check if object exists in root namespace
        """
        if name in root:
            # Copy the object from the database
            obj = copy.deepcopy(root[name])
        else:
            # Return False if the object does not exist in the database
            obj = False
        connection.close()
        return obj
        """

class HelperLogRegressionPerfAnalytics:
    def __init__(self):
        # Hallo
        print("Hallo")

