from time import sleep
from typing import List
from message import IDSHTTPMessage
from stages import Stage
from dtos import DTO, TypingExtractionDTO
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
        super().__init__(successor)

    def run(self, dto: DTO) -> None:
        if not isinstance(dto, TypingExtractionDTO):
            sys.exit("Typing: FilterTypingDTO required.")
        features = {}
        for plugin in self.plugins:
            temp_features = plugin.extract_features(dto.message, dto.type)
            features.update(temp_features)
        #print(features)
        
        if self.mode == 'train' and dto.type.has_body:
            # Add the body n-gram information to the database for future calculations
            counter_body_monograms = Counter(features['body_monograms'])
            counter_body_bigrams = Counter(features['body_bigrams'])
            counter_body_hexagrams = Counter(features['body_hexagrams'])

            db_body_ngrams = self.db_handler.get_object("body_ngrams")

            if not dto.type in db_body_ngrams:
                db_body_ngrams[dto.type] = {
                    "monograms": [],
                    "bigrams": [],
                    "hexagrams": []
                }
            db_body_ngrams[dto.type]["monograms"].append((datetime.now(), counter_body_monograms))
            db_body_ngrams[dto.type]["bigrams"].append((datetime.now(), counter_body_bigrams))
            db_body_ngrams[dto.type]["hexagrams"].append((datetime.now(), counter_body_hexagrams))

            thread = threading.Thread(target=self.db_handler.write_object, args=("body_ngrams", db_body_ngrams))
            thread.start()

            del features['body_monograms']
            del features['body_bigrams']
            del features['body_hexagrams']

        if self.mode == 'train' and dto.type.has_query:
            # Add the query n-gram information to the database for future calculations
            counter_query_monograms = Counter(features['query_monograms'])
            counter_query_bigrams = Counter(features['query_bigrams'])
            counter_query_hexagrams = Counter(features['query_hexagrams'])

            db_query_ngrams = self.db_handler.get_object("query_ngrams")

            if not dto.type in db_query_ngrams:
                db_query_ngrams[dto.type] = {
                    "monograms": [],
                    "bigrams": [],
                    "hexagrams": []
                }
            db_query_ngrams[dto.type]["monograms"].append((datetime.now(), counter_query_monograms))
            db_query_ngrams[dto.type]["bigrams"].append((datetime.now(), counter_query_bigrams))
            db_query_ngrams[dto.type]["hexagrams"].append((datetime.now(), counter_query_hexagrams))

            thread = threading.Thread(target=self.db_handler.write_object, args=("query_ngrams", db_query_ngrams))
            thread.start()

            del features['query_monograms']
            del features['query_bigrams']
            del features['query_hexagrams']
        
        """
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
        """
