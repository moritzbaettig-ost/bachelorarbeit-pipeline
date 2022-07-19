from time import sleep
from typing import List
from message import IDSHTTPMessage
from stages import Stage
from dtos import DTO, TypingExtractionDTO, ExtractionModelDTO
import sys
from type import Type
import os
import importlib
from collections import Counter
from datetime import datetime
from database import Database
import threading


class ExtractionPluginInterface:
    def extract_features(self, message: IDSHTTPMessage, type: Type) -> List:
        pass


class Extraction(Stage):
    def __init__(self, successor: 'Stage', mode: str, logging: bool, db_handler: Database):
        self.successor = successor
        if len(os.listdir('./stages/extraction/plugins')) == 0:
            sys.exit("No extraction plugin detected. Please place default extraction plugin in the extraction plugin directory.")
        sys.path.append('./stages/extraction/plugins')
        self.plugins = [
            importlib.import_module(f.split('.')[0], '.').Plugin()
            for f in next(os.walk('stages/extraction/plugins'))[2]
        ]
        self.mode = mode
        self.logging = logging
        self.db_handler = db_handler

    def run(self, dto: DTO) -> None:
        if not isinstance(dto, TypingExtractionDTO):
            sys.exit("Typing: FilterTypingDTO required.")
        features = {}
        for plugin in self.plugins:
            temp_features = plugin.extract_features(dto.message, dto.type, self.mode, self.db_handler)
            features.update(temp_features)
        #print(features)
        
        if self.mode == "train":
            # Save everything in the db so the ML model can use the data for training
            data = {
                "timestamp": datetime.now(),
                "features": features,
                "message": dto.message,
                "type": dto.type,
                "label": 1
            }
            
            db_data = self.db_handler.get_object("data")
            db_data.append(data)
            thread = threading.Thread(target=self.db_handler.write_object, args=("data", db_data))
            thread.start()

        new_dto = ExtractionModelDTO(features=features, type=dto.type)
        self.successor.run(new_dto)
