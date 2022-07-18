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

            current_body_monogram_pool_counter = Counter()
            for t in db_body_ngrams[dto.type]["monograms"]:
                current_body_monogram_pool_counter = current_body_monogram_pool_counter + t[1]
            current_body_monogram_pool = dict(current_body_monogram_pool_counter)
            current_body_bigram_pool_counter = Counter()
            for t in db_body_ngrams[dto.type]["bigrams"]:
                current_body_bigram_pool_counter = current_body_bigram_pool_counter + t[1]
            current_body_bigram_pool = dict(current_body_bigram_pool_counter)
            current_body_hexagram_pool_counter = Counter()
            for t in db_body_ngrams[dto.type]["hexagrams"]:
                current_body_hexagram_pool_counter = current_body_hexagram_pool_counter + t[1]
            current_body_hexagram_pool = dict(current_body_hexagram_pool_counter)

            factor_monograms = 1.0/sum(current_body_monogram_pool.values())
            factor_bigrams = 1.0/sum(current_body_bigram_pool.values())
            factor_hexagrams = 1.0/sum(current_body_hexagram_pool.values())
            
            remove_monograms = []
            remove_bigrams = []
            remove_hexagrams = []
            for key in current_body_monogram_pool:
                if current_body_monogram_pool[key]*factor_monograms > 0.0001:
                    current_body_monogram_pool[key] = current_body_monogram_pool[key]*factor_monograms
                else:
                    remove_monograms.append(key)
            for i in range(len(remove_monograms)):
                current_body_monogram_pool.pop(remove_monograms[i])
            for key in current_body_bigram_pool:
                if current_body_bigram_pool[key]*factor_bigrams > 0.0001:
                    current_body_bigram_pool[key] = current_body_bigram_pool[key]*factor_bigrams
                else:
                    remove_bigrams.append(key)
            for i in range(len(remove_bigrams)):
                current_body_bigram_pool.pop(remove_bigrams[i])
            for key in current_body_hexagram_pool:
                if current_body_hexagram_pool[key]*factor_hexagrams > 0.0001:
                    current_body_hexagram_pool[key] = current_body_hexagram_pool[key]*factor_hexagrams
                else:
                    remove_hexagrams.append(key)
            for i in range(len(remove_hexagrams)):
                current_body_hexagram_pool.pop(remove_hexagrams[i])

            occurrence_monograms = 0
            occurrence_bigrams = 0
            occurrence_hexagrams = 0
            for key in features['body_monograms']:
                if key in current_body_monogram_pool:
                    occurrence_monograms = occurrence_monograms + features['body_monograms'][key]
            for key in features['body_bigrams']:
                if key in current_body_bigram_pool:
                    occurrence_bigrams = occurrence_bigrams + features['body_bigrams'][key]
            for key in features['body_hexagrams']:
                if key in current_body_hexagram_pool:
                    occurrence_hexagrams = occurrence_hexagrams + features['body_hexagrams'][key]

            features['body_monograms'] = float(occurrence_monograms)/float(sum(features['body_monograms'].values()))
            features['body_bigrams'] = float(occurrence_bigrams)/float(sum(features['body_bigrams'].values()))
            features['body_hexagrams'] = float(occurrence_hexagrams)/float(sum(features['body_hexagrams'].values()))

            thread = threading.Thread(target=self.db_handler.write_object, args=("body_ngrams", db_body_ngrams))
            thread.start()

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

            current_query_monogram_pool_counter = Counter()
            for t in db_query_ngrams[dto.type]["monograms"]:
                current_query_monogram_pool_counter = current_query_monogram_pool_counter + t[1]
            current_query_monogram_pool = dict(current_query_monogram_pool_counter)
            current_query_bigram_pool_counter = Counter()
            for t in db_query_ngrams[dto.type]["bigrams"]:
                current_query_bigram_pool_counter = current_query_bigram_pool_counter + t[1]
            current_query_bigram_pool = dict(current_query_bigram_pool_counter)
            current_query_hexagram_pool_counter = Counter()
            for t in db_query_ngrams[dto.type]["hexagrams"]:
                current_query_hexagram_pool_counter = current_query_hexagram_pool_counter + t[1]
            current_query_hexagram_pool = dict(current_query_hexagram_pool_counter)

            factor_monograms = 1.0/sum(current_query_monogram_pool.values())
            factor_bigrams = 1.0/sum(current_query_bigram_pool.values())
            factor_hexagrams = 1.0/sum(current_query_hexagram_pool.values())
            
            remove_monograms = []
            remove_bigrams = []
            remove_hexagrams = []
            for key in current_query_monogram_pool:
                if current_query_monogram_pool[key]*factor_monograms > 0.0001:
                    current_query_monogram_pool[key] = current_query_monogram_pool[key]*factor_monograms
                else:
                    remove_monograms.append(key)
            for i in range(len(remove_monograms)):
                current_query_monogram_pool.pop(remove_monograms[i])
            for key in current_query_bigram_pool:
                if current_query_bigram_pool[key]*factor_bigrams > 0.0001:
                    current_query_bigram_pool[key] = current_query_bigram_pool[key]*factor_bigrams
                else:
                    remove_bigrams.append(key)
            for i in range(len(remove_bigrams)):
                current_query_bigram_pool.pop(remove_bigrams[i])
            for key in current_query_hexagram_pool:
                if current_query_hexagram_pool[key]*factor_hexagrams > 0.0001:
                    current_query_hexagram_pool[key] = current_query_hexagram_pool[key]*factor_hexagrams
                else:
                    remove_hexagrams.append(key)
            for i in range(len(remove_hexagrams)):
                current_query_hexagram_pool.pop(remove_hexagrams[i])

            occurrence_monograms = 0
            occurrence_bigrams = 0
            occurrence_hexagrams = 0
            for key in features['query_monograms']:
                if key in current_query_monogram_pool:
                    occurrence_monograms = occurrence_monograms + features['query_monograms'][key]
            for key in features['query_bigrams']:
                if key in current_query_bigram_pool:
                    occurrence_bigrams = occurrence_bigrams + features['query_bigrams'][key]
            for key in features['query_hexagrams']:
                if key in current_query_hexagram_pool:
                    occurrence_hexagrams = occurrence_hexagrams + features['query_hexagrams'][key]

            features['query_monograms'] = float(occurrence_monograms)/float(sum(features['query_monograms'].values()))
            features['query_bigrams'] = float(occurrence_bigrams)/float(sum(features['query_bigrams'].values()))
            features['query_hexagrams'] = float(occurrence_hexagrams)/float(sum(features['query_hexagrams'].values()))

            thread = threading.Thread(target=self.db_handler.write_object, args=("query_ngrams", db_query_ngrams))
            thread.start()
        
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
