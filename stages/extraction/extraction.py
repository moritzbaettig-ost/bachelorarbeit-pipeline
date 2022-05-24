from typing import List
from message import IDSHTTPMessage
from stages import Stage
from dtos import DTO, TypingExtractionDTO
import sys
from type import Type
import os
import importlib


class ExtractionPluginInterface:
    def extract_features(self, message: IDSHTTPMessage, type: Type) -> List:
        pass


class Extraction(Stage):
    def __init__(self, successor: 'Stage'):
        if len(os.listdir('./stages/extraction/plugins')) == 0:
            sys.exit("No extraction plugin detected. Please place default extraction plugin in the extraction plugin directory.")
        sys.path.append('./stages/extraction/plugins')
        self.plugins = [
            importlib.import_module(f.split('.')[0], '.').Plugin()
            for f in next(os.walk('stages/extraction/plugins'))[2]
        ]
        super().__init__(successor)

    def run(self, dto: DTO) -> None:
        if not isinstance(dto, TypingExtractionDTO):
            sys.exit("Typing: FilterTypingDTO required.")
        features = []
        for plugin in self.plugins:
            temp_features = plugin.extract_features(dto.message, dto.type)
            features = features + temp_features
        # TODO: Extraction Stage based on type
        #print(features)
