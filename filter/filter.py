import importlib
import sys


class RequestFilter:
    def __init__(self, successor, filter_plugin):
        sys.path.append('./filter')
        self._successor = successor
        if filter_plugin is not None:
            self._plugin = importlib.import_module('filterPlugin'+filter_plugin, ".").Plugin()
        else:
            self._plugin = importlib.import_module('filterPluginDefault', ".").Plugin()

    def filter_request(self, req):
        # TODO: Pass return string to successor
        print(self._plugin.filter_request(req))


class FilterPluginInterface:
    def filter_request(self, req: str) -> str:
        pass
