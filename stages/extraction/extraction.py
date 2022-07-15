from typing import List
from message import IDSHTTPMessage
from stages import Stage
from dtos import DTO, TypingExtractionDTO
import sys
from type import Type
import os
import importlib
import ZODB, ZODB.FileStorage
import transaction


class ExtractionPluginInterface:
    def extract_features(self, message: IDSHTTPMessage, type: Type) -> List:
        pass


class Extraction(Stage):
    def __init__(self, successor: 'Stage', mode: str, logging: bool):
        if len(os.listdir('./stages/extraction/plugins')) == 0:
            sys.exit("No extraction plugin detected. Please place default extraction plugin in the extraction plugin directory.")
        sys.path.append('./stages/extraction/plugins')
        self.plugins = [
            importlib.import_module(f.split('.')[0], '.').Plugin()
            for f in next(os.walk('stages/extraction/plugins'))[2]
        ]
        self.mode = mode
        self.logging = logging
        super().__init__(successor)

    def run(self, dto: DTO) -> None:
        if not isinstance(dto, TypingExtractionDTO):
            sys.exit("Typing: FilterTypingDTO required.")
        features = {}
        for plugin in self.plugins:
            temp_features = plugin.extract_features(dto.message, dto.type)
            features.update(temp_features)
        print(features)
        
        if self.mode == 'train':
            # Add the n-gram information to the database for future calculations
            # TODO
            pass
        
        if self.logging:
            # Save the feature dict in the database with the type as key
            storage = ZODB.FileStorage.FileStorage('db.fs')
            db = ZODB.DB(storage)
            connection = db.open()
            root = connection.root()
            if not "features" in root:
                root["features"] = {}
            db_features = root["features"]

            if not dto.type in db_features:
                db_features[dto.type] = []
            db_features[dto.type].append(features)

            root["features"] = db_features
            transaction.commit()
            #print(root.items())
            connection.close()
