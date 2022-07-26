from typing import Dict
from stages.extraction import ExtractionPluginInterface
from message import IDSHTTPMessage
from type import Type
from sklearn.feature_extraction.text import CountVectorizer
from collections import Counter
from datetime import datetime
from database import DatabaseHandler, DatabaseHandlerStrategy
from BTrees.OOBTree import BTree
import transaction
import persistent.list
import ZODB.DB
import queue


class ExtractionPluginDefaultStrategy(DatabaseHandlerStrategy):
    def __init__(self, db: ZODB.DB, queue: queue.Queue) -> None:
        self.db = db
        self.queue = queue
        connection = self.db.open()
        root = connection.root()
        if not "body_ngrams" in root:
            root["body_ngrams"] = BTree()
        if not "query_ngrams" in root:
            root["query_ngrams"] = BTree()
        transaction.commit()
        connection.close()


    def write(self, data: object, name: str, type: Type) -> None:
        item = {
            "worker_method": self._write_worker,
            "name": name,
            "object": data,
            "type": type
        }
        self.queue.put(item)


    def read(self, name: str, type: Type) -> object:
        connection = self.db.open()
        root = connection.root()
        if not root[name].has_key(type):
            root[name].insert(type, {
                    "monograms": persistent.list.PersistentList(),
                    "bigrams": persistent.list.PersistentList(),
                    "hexagrams": persistent.list.PersistentList()
                })
            transaction.commit()
        res =  {
            "monograms": list(root[name][type]["monograms"]),
            "bigrams": list(root[name][type]["bigrams"]),
            "hexagrams": list(root[name][type]["hexagrams"])
        }
        connection.close()
        return res


    def _write_worker(self, item: dict) -> None:
        connection = self.db.open()
        root = connection.root()
        obj = item["object"]
        (root[item["name"]].get(item["type"]))["monograms"].append(obj["monograms"])
        (root[item["name"]].get(item["type"]))["bigrams"].append(obj["bigrams"])
        (root[item["name"]].get(item["type"]))["hexagrams"].append(obj["hexagrams"])
        transaction.commit()
        connection.close()


class Plugin(ExtractionPluginInterface):
    """
    This class represents a plugin for the extraction stage that implements the default feature extraction.

    Methods
    ----------
    extract_features(message, type, mode, db_handler)
        This method extracts and returns the features for the following ML-algorithm based on the type.
    get_ngram_dict(n, data)
        This method calculates the n-gram for a specific string.
    """

    def __init__(self, db_handler: DatabaseHandler) -> None:
        self.strategy = ExtractionPluginDefaultStrategy(db_handler.db, db_handler.queue)


    def extract_features(self, message: IDSHTTPMessage, type: Type, mode: str, db_handler: DatabaseHandler) -> Dict:
        """
        This method extracts and returns the features for the following ML-algorithm based on the type.

        Parameters
        ----------
        message: IDSHTTPMessage
            The HTTP message from which the features should be extracted.
        type: Type
            The type of the HTTP message.
        mode: str
            The mode of the pipeline.
        db_handler: DatabaseHandler
            The database handler.

        Returns
        ----------
        list
            The list of the extracted features.
        """

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

            db_handler.set_strategy(self.strategy)
            db_query_ngrams = db_handler.read("query_ngrams", type)
            if mode == "train":
                # Add the query n-gram information to the database for future calculations
                db_handler.set_strategy(self.strategy)
                db_handler.write({
                    "monograms": (datetime.now(), counter_query_monograms),
                    "bigrams": (datetime.now(), counter_query_bigrams),
                    "hexagrams": (datetime.now(), counter_query_hexagrams)
                }, "query_ngrams", type)

            db_query_ngrams["monograms"].append((datetime.now(), counter_query_monograms))
            db_query_ngrams["bigrams"].append((datetime.now(), counter_query_bigrams))
            db_query_ngrams["hexagrams"].append((datetime.now(), counter_query_hexagrams))

            current_query_monogram_pool_counter = Counter()
            for t in db_query_ngrams["monograms"]:
                current_query_monogram_pool_counter = current_query_monogram_pool_counter + t[1]
            current_query_monogram_pool = dict(current_query_monogram_pool_counter)
            current_query_bigram_pool_counter = Counter()
            for t in db_query_ngrams["bigrams"]:
                current_query_bigram_pool_counter = current_query_bigram_pool_counter + t[1]
            current_query_bigram_pool = dict(current_query_bigram_pool_counter)
            current_query_hexagram_pool_counter = Counter()
            for t in db_query_ngrams["hexagrams"]:
                current_query_hexagram_pool_counter = current_query_hexagram_pool_counter + t[1]
            current_query_hexagram_pool = dict(current_query_hexagram_pool_counter)

            if sum(current_query_monogram_pool.values()) > 0:
                factor_monograms = 1.0/sum(current_query_monogram_pool.values())
            else:
                factor_monograms = 0.0
            if sum(current_query_bigram_pool.values()) > 0:
                factor_bigrams = 1.0/sum(current_query_bigram_pool.values())
            else:
                factor_bigrams = 0.0
            if sum(current_query_hexagram_pool.values()) > 0:
                factor_hexagrams = 1.0/sum(current_query_hexagram_pool.values())
            else:
                factor_hexagrams = 0.0
            
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

            if float(sum(dictRequest['query_monograms'].values()))>0:
                dictRequest['query_monograms'] = float(occurrence_monograms)/float(sum(dictRequest['query_monograms'].values()))
            else:
                dictRequest['query_monograms'] = 0.0
            if float(sum(dictRequest['query_bigrams'].values()))>0:
                dictRequest['query_bigrams'] = float(occurrence_bigrams)/float(sum(dictRequest['query_bigrams'].values()))
            else:
                dictRequest['query_bigrams'] = 0.0
            if float(sum(dictRequest['query_hexagrams'].values()))>0:
                dictRequest['query_hexagrams'] = float(occurrence_hexagrams)/float(sum(dictRequest['query_hexagrams'].values()))
            else:
                dictRequest['query_hexagrams'] = 0.0

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

            db_handler.set_strategy(self.strategy)
            db_body_ngrams = db_handler.read("body_ngrams", type)
            if mode == "train":
                # Add the body n-gram information to the database for future calculations
                db_handler.set_strategy(self.strategy)
                db_handler.write({
                    "monograms": (datetime.now(), counter_body_monograms),
                    "bigrams": (datetime.now(), counter_body_bigrams),
                    "hexagrams": (datetime.now(), counter_body_hexagrams)
                }, "body_ngrams", type)

            db_body_ngrams["monograms"].append((datetime.now(), counter_body_monograms))
            db_body_ngrams["bigrams"].append((datetime.now(), counter_body_bigrams))
            db_body_ngrams["hexagrams"].append((datetime.now(), counter_body_hexagrams))

            current_body_monogram_pool_counter = Counter()
            for t in db_body_ngrams["monograms"]:
                current_body_monogram_pool_counter = current_body_monogram_pool_counter + t[1]
            current_body_monogram_pool = dict(current_body_monogram_pool_counter)
            current_body_bigram_pool_counter = Counter()
            for t in db_body_ngrams["bigrams"]:
                current_body_bigram_pool_counter = current_body_bigram_pool_counter + t[1]
            current_body_bigram_pool = dict(current_body_bigram_pool_counter)
            current_body_hexagram_pool_counter = Counter()
            for t in db_body_ngrams["hexagrams"]:
                current_body_hexagram_pool_counter = current_body_hexagram_pool_counter + t[1]
            current_body_hexagram_pool = dict(current_body_hexagram_pool_counter)

            if sum(current_body_monogram_pool.values()) > 0:
                factor_monograms = 1.0/sum(current_body_monogram_pool.values())
            else:
                factor_monograms = 0.0
            if sum(current_body_bigram_pool.values()) > 0:
                factor_bigrams = 1.0/sum(current_body_bigram_pool.values())
            else:
                factor_bigrams = 0.0
            if sum(current_body_hexagram_pool.values()) > 0:
                factor_hexagrams = 1.0/sum(current_body_hexagram_pool.values())
            else:
                factor_hexagrams = 0.0
            
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

            if float(sum(dictRequest['body_monograms'].values()))>0:
                dictRequest['body_monograms'] = float(occurrence_monograms)/float(sum(dictRequest['body_monograms'].values()))
            else:
                dictRequest['body_monograms'] = 0.0
            if float(sum(dictRequest['body_bigrams'].values()))>0:
                dictRequest['body_bigrams'] = float(occurrence_bigrams)/float(sum(dictRequest['body_bigrams'].values()))
            else:
                dictRequest['body_bigrams'] = 0.0
            if float(sum(dictRequest['body_hexagrams'].values()))>0:
                dictRequest['body_hexagrams'] = float(occurrence_hexagrams)/float(sum(dictRequest['body_hexagrams'].values()))
            else:
                dictRequest['body_hexagrams'] = 0.0

        return dictRequest


    def get_ngram_dict(self, n, data) -> dict:
        """
        This method calculates the n-gram for a specific string.

        Parameters
        ----------
        n: int
            The type of the n-gram (monogram, bigram, ...)
        data: str
            The string to be analyzed

        Returns
        ----------
        dict
            The dictionary with the n-grams as keys and the occurance as values.
        """
        
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
