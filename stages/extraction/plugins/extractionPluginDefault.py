from typing import Dict
from stages.extraction import ExtractionPluginInterface
from message import IDSHTTPMessage
from type import Type
from sklearn.feature_extraction.text import CountVectorizer
from collections import Counter
from datetime import datetime
import threading
from database import Database


class Plugin(ExtractionPluginInterface):
    def extract_features(self, message: IDSHTTPMessage, type: Type, mode: str, db_handler: Database) -> Dict:
        dictRequest = {}
        # Basic information
        dictRequest['source_address'] = message.source_address
        dictRequest['method'] = message.method
        dictRequest['path'] = message.path
        dictRequest['protocol_version'] = message.protocol_version
        dictRequest['length'] = len(message)

        # Header information
        for entry in message.header:
            dictRequest[entry] = message.header[entry]

        dictRequest['basic_feature_count'] = len(dictRequest.keys())

        # Query
        if type.has_query:
            dictRequest['path_query'] = message.query
            dictRequest['path_feature_count'] = len(message.query.split('&'))
            count_lower = 0
            count_upper = 0
            count_numeric = 0
            count_spaces = 0
            count_specialchar = 0
            for i in message.query:
                if (i.islower()):
                    count_lower = count_lower + 1
                if (i.isupper()):
                    count_upper = count_upper + 1
                if (i.isnumeric()):
                    count_numeric = count_numeric + 1
                if (i.isspace()):
                    count_spaces = count_spaces + 1
                if ((48 > ord(i)) or (ord(i) > 57 and ord(i) < 65) or (ord(i) > 90 and ord(i) < 97) or (ord(i) > 122)):
                    count_specialchar = count_specialchar + 1
            dictRequest['path_query_lower'] = count_lower
            dictRequest['path_query_upper'] = count_upper
            dictRequest['path_query_numeric'] = count_numeric
            dictRequest['path_query_spaces'] = count_spaces
            dictRequest['path_query_specialchar'] = count_specialchar

            dictRequest['query_monograms'] = self.get_ngram_dict(1, message.query)
            dictRequest['query_bigrams'] = self.get_ngram_dict(2, message.query)
            dictRequest['query_hexagrams'] = self.get_ngram_dict(6, message.query)

            counter_query_monograms = Counter(dictRequest['query_monograms'])
            counter_query_bigrams = Counter(dictRequest['query_bigrams'])
            counter_query_hexagrams = Counter(dictRequest['query_hexagrams'])

            db_query_ngrams = db_handler.get_object("query_ngrams")

            if not type in db_query_ngrams:
                db_query_ngrams[type] = {
                    "monograms": [],
                    "bigrams": [],
                    "hexagrams": []
                }
            db_query_ngrams[type]["monograms"].append((datetime.now(), counter_query_monograms))
            db_query_ngrams[type]["bigrams"].append((datetime.now(), counter_query_bigrams))
            db_query_ngrams[type]["hexagrams"].append((datetime.now(), counter_query_hexagrams))

            current_query_monogram_pool_counter = Counter()
            for t in db_query_ngrams[type]["monograms"]:
                current_query_monogram_pool_counter = current_query_monogram_pool_counter + t[1]
            current_query_monogram_pool = dict(current_query_monogram_pool_counter)
            current_query_bigram_pool_counter = Counter()
            for t in db_query_ngrams[type]["bigrams"]:
                current_query_bigram_pool_counter = current_query_bigram_pool_counter + t[1]
            current_query_bigram_pool = dict(current_query_bigram_pool_counter)
            current_query_hexagram_pool_counter = Counter()
            for t in db_query_ngrams[type]["hexagrams"]:
                current_query_hexagram_pool_counter = current_query_hexagram_pool_counter + t[1]
            current_query_hexagram_pool = dict(current_query_hexagram_pool_counter)

            if mode == "train":
                # Add the query n-gram information to the database for future calculations
                thread = threading.Thread(target=db_handler.write_object, args=("query_ngrams", db_query_ngrams))
                thread.start()

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
            for key in dictRequest['query_monograms']:
                if key in current_query_monogram_pool:
                    occurrence_monograms = occurrence_monograms + dictRequest['query_monograms'][key]
            for key in dictRequest['query_bigrams']:
                if key in current_query_bigram_pool:
                    occurrence_bigrams = occurrence_bigrams + dictRequest['query_bigrams'][key]
            for key in dictRequest['query_hexagrams']:
                if key in current_query_hexagram_pool:
                    occurrence_hexagrams = occurrence_hexagrams + dictRequest['query_hexagrams'][key]

            dictRequest['query_monograms'] = float(occurrence_monograms)/float(sum(dictRequest['query_monograms'].values()))
            dictRequest['query_bigrams'] = float(occurrence_bigrams)/float(sum(dictRequest['query_bigrams'].values()))
            dictRequest['query_hexagrams'] = float(occurrence_hexagrams)/float(sum(dictRequest['query_hexagrams'].values()))

        # Body
        if type.has_body:
            dictRequest['body'] = message.body

            count_lower = 0
            count_upper = 0
            count_numeric = 0
            count_spaces = 0
            count_specialchar = 0
            for i in message.body:
                if (i.islower()):
                    count_lower = count_lower + 1
                if (i.isupper()):
                    count_upper = count_upper + 1
                if (i.isnumeric()):
                    count_numeric = count_numeric + 1
                if (i.isspace()):
                    count_spaces = count_spaces + 1
                if ((48 > ord(i)) or (ord(i) > 57 and ord(i) < 65) or (ord(i) > 90 and ord(i) < 97) or (ord(i) > 122)):
                    count_specialchar = count_specialchar + 1
            dictRequest['body_lower'] = count_lower
            dictRequest['body_upper'] = count_upper
            dictRequest['body_numeric'] = count_numeric
            dictRequest['body_spaces'] = count_spaces
            dictRequest['body_specialchar'] = count_specialchar

            dictRequest['body_monograms'] = self.get_ngram_dict(1, message.body)
            dictRequest['body_bigrams'] = self.get_ngram_dict(2, message.body)
            dictRequest['body_hexagrams'] = self.get_ngram_dict(6, message.body)

            counter_body_monograms = Counter(dictRequest['body_monograms'])
            counter_body_bigrams = Counter(dictRequest['body_bigrams'])
            counter_body_hexagrams = Counter(dictRequest['body_hexagrams'])

            db_body_ngrams = db_handler.get_object("body_ngrams")

            if not type in db_body_ngrams:
                db_body_ngrams[type] = {
                    "monograms": [],
                    "bigrams": [],
                    "hexagrams": []
                }
            db_body_ngrams[type]["monograms"].append((datetime.now(), counter_body_monograms))
            db_body_ngrams[type]["bigrams"].append((datetime.now(), counter_body_bigrams))
            db_body_ngrams[type]["hexagrams"].append((datetime.now(), counter_body_hexagrams))

            current_body_monogram_pool_counter = Counter()
            for t in db_body_ngrams[type]["monograms"]:
                current_body_monogram_pool_counter = current_body_monogram_pool_counter + t[1]
            current_body_monogram_pool = dict(current_body_monogram_pool_counter)
            current_body_bigram_pool_counter = Counter()
            for t in db_body_ngrams[type]["bigrams"]:
                current_body_bigram_pool_counter = current_body_bigram_pool_counter + t[1]
            current_body_bigram_pool = dict(current_body_bigram_pool_counter)
            current_body_hexagram_pool_counter = Counter()
            for t in db_body_ngrams[type]["hexagrams"]:
                current_body_hexagram_pool_counter = current_body_hexagram_pool_counter + t[1]
            current_body_hexagram_pool = dict(current_body_hexagram_pool_counter)

            if mode == "train":
                # Add the body n-gram information to the database for future calculations
                thread = threading.Thread(target=db_handler.write_object, args=("body_ngrams", db_body_ngrams))
                thread.start()

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
            for key in dictRequest['body_monograms']:
                if key in current_body_monogram_pool:
                    occurrence_monograms = occurrence_monograms + dictRequest['body_monograms'][key]
            for key in dictRequest['body_bigrams']:
                if key in current_body_bigram_pool:
                    occurrence_bigrams = occurrence_bigrams + dictRequest['body_bigrams'][key]
            for key in dictRequest['body_hexagrams']:
                if key in current_body_hexagram_pool:
                    occurrence_hexagrams = occurrence_hexagrams + dictRequest['body_hexagrams'][key]

            dictRequest['body_monograms'] = float(occurrence_monograms)/float(sum(dictRequest['body_monograms'].values()))
            dictRequest['body_bigrams'] = float(occurrence_bigrams)/float(sum(dictRequest['body_bigrams'].values()))
            dictRequest['body_hexagrams'] = float(occurrence_hexagrams)/float(sum(dictRequest['body_hexagrams'].values()))

        return dictRequest

    def get_ngram_dict(self, n, data) -> dict:
        # Check if data can be vectorized
        if n <= len(data):
            vectorizer = CountVectorizer(ngram_range=(n, n), analyzer='char')
            ngrams = vectorizer.fit_transform([data])
            ngrams = ngrams.toarray()[0]
            ngram_features = vectorizer.get_feature_names_out()
            ngrams_freq = {}
            for tag, count in zip(ngram_features, ngrams):
                ngrams_freq[tag] = count
            return ngrams_freq
        else:
            return {}
