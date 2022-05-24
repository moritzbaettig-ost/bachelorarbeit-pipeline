from typing import List
from stages.extraction import ExtractionPluginInterface
from message import IDSHTTPMessage
from type import Type


class Plugin(ExtractionPluginInterface):
    def extract_features(self, message: IDSHTTPMessage, type: Type) -> List:
        return ['test1', 'test2']