import pathlib
import sys

from matplotlib import pyplot as plt
from sklearn.feature_extraction.text import CountVectorizer

directory = pathlib.Path(__file__)
sys.path.append(directory.parent.parent.parent.__str__())

import os
import re
import pandas as pd

HTTP_RE = re.compile(r"ST@RT.+?INFO\s+(.+?)\s+END", re.MULTILINE | re.DOTALL)


def http_re(data):
    """
    Extracts HTTP requests from raw data string in special logging format.

    Logging format `ST@RT\n%(asctime)s %(levelname)-8s\n%(message)s\nEND`
    where `message` is a required HTTP request bytes.
    """

    return HTTP_RE.findall(data)


def get_requests_from_file(path):
    """
    Reads raw HTTP requests from given file.
    """
    with open(path, 'r') as f:
        file_data = f.read()
    requests = http_re(file_data)
    return requests


def _process_request(req):
    """
    Splits a request into lines and convert a string into ints.
    """
    my_method = ""
    my_uri = "http://127.0.0.1:80"
    dictRequest={}
    my_header = {}
    i = 0
    body = False
    for line in req.splitlines():
        if line=="":
            body=True
        if i == 0 and len(line.split())>2:
            my_method=line.split()[0]
            my_uri = my_uri + line.split()[1]
        else:
            if not body and len(line.split(':'))>1:
                key = line.split(':')[0].lstrip()
                value = line.split(':')[1].lstrip()
                my_header[key]=value
            else:
                dictRequest['body']=line.split(':')[0]
        #print("-")
        i=i+1
    return my_method, my_uri, my_header, dictRequest

def print_histogram():

    script_dir = os.path.dirname(__file__)  # <-- absolute dir the script is in
    rel_path_train = "vulnbank_train.txt"
    rel_path_anomaly = "vulnbank_anomaly.txt"
    path_normal_data = os.path.join(script_dir, rel_path_train)
    path_anomaly_data = os.path.join(script_dir, rel_path_anomaly)

    http_requests_normal = get_requests_from_file(path_normal_data)
    http_requests_anomaly = get_requests_from_file(path_anomaly_data)
    print(f"# of normal requests: {str(len(http_requests_normal))}")
    ngram_query_list = []
    ngram_body_list = []
    for r in http_requests_normal:
        if len(_process_request(r)[1].split('?'))>1:
            ngram_query_list.append(_process_request(r)[1].split('?')[1])
        if 'body' in dict(_process_request(r)[3]):
            if str(dict(_process_request(r)[3]).get('body')).find('User-Agent')==-1 and str(dict(_process_request(r)[3]).get('body')).find('Accept-Language')==-1:
                ngram_body_list.append(str(dict(_process_request(r)[3]).get('body')))
    #print(len(ngram_query_list))
    #print(ngram_body_list)
    ngrams_freq_normal = {}
    for i in range(0,len(ngram_body_list)):
        if 6 <= len(ngram_body_list[i]):
            vectorizer = CountVectorizer(ngram_range=(6, 6), analyzer='char')
            ngrams = vectorizer.fit_transform([ngram_body_list[i]])
            ngrams = ngrams.toarray()[0]
            ngram_features = vectorizer.get_feature_names_out()
            for tag, count in zip(ngram_features, ngrams):
                if tag in ngrams_freq_normal:
                    ngrams_freq_normal[tag] = int(ngrams_freq_normal.get(tag))+int(count)
                else:
                    ngrams_freq_normal[tag] = int(count)
    for key, value in ngrams_freq_normal.items():
        ngrams_freq_normal[key]=ngrams_freq_normal[key]/len(ngram_body_list)
    ngrams_freq_normal=dict(sorted(ngrams_freq_normal.items(), key=lambda item: item[1], reverse=True))
    #print(ngrams_freq)

    print(ngrams_freq_normal)
    ngrams_freq = ngrams_freq_normal.copy()
    for key, value in ngrams_freq.items():
        ngrams_freq[key] = 0

    print(f"# of anomaly requests: {str(len(http_requests_anomaly))}")
    ngram_query_list_attack = []
    ngram_body_list_attack = []
    for r in http_requests_anomaly:
        if len(_process_request(r)[1].split('?'))>1:
            ngram_query_list_attack.append(_process_request(r)[1].split('?')[1])
        if 'body' in dict(_process_request(r)[3]):
            if str(dict(_process_request(r)[3]).get('body')).find('User-Agent')==-1 and str(dict(_process_request(r)[3]).get('body')).find('Accept-Language')==-1:
                ngram_body_list_attack.append(str(dict(_process_request(r)[3]).get('body')))
    #print(len(ngram_query_list_attack))
    #print(ngram_body_list_attack)
    for i in range(0,len(ngram_body_list_attack)):
        if 6 <= len(ngram_body_list_attack[i]):
            vectorizer = CountVectorizer(ngram_range=(6, 6), analyzer='char')
            ngrams = vectorizer.fit_transform([ngram_body_list_attack[i]])
            ngrams = ngrams.toarray()[0]
            ngram_features = vectorizer.get_feature_names_out()
            for tag, count in zip(ngram_features, ngrams):
                if tag in ngrams_freq:
                    ngrams_freq[tag] = int(ngrams_freq.get(tag))+int(count)
                else:
                    ngrams_freq[tag] = int(count)
    #print(ngrams_freq)
    for key, value in ngrams_freq.items():
        ngrams_freq[key]=ngrams_freq[key]/len(ngram_body_list_attack)
    plt.bar(ngrams_freq.keys(), ngrams_freq.values(), color='r')
    plt.ylim(0,1.01)
    plt.title('Visualisierung der Body-6-Gramme im anomalen Datensatz')
    plt.ylabel('Normalisierte Häufigkeit')
    plt.xlabel('6-Gramme')
    plt.tick_params(
        axis='x',  # changes apply to the x-axis
        which='both',  # both major and minor ticks are affected
        bottom=False,  # ticks along the bottom edge are off
        top=False,  # ticks along the top edge are off
        labelbottom=False)  # labels along the bottom edge are off
    plt.show()
    print(ngrams_freq)
    ngram_temp = ngrams_freq.copy()
    for key, value in ngram_temp.items():
        ngram_temp[key]=0

    for key, value in ngrams_freq_normal.items():
        print("Hallo")
        ngram_temp[key]=ngrams_freq_normal[key]
    print(ngram_temp)
    plt.bar(ngram_temp.keys(), ngram_temp.values(), color='g')
    plt.ylim(0,1.01)
    plt.title('Visualisierung der Body-6-Gramme im normalen Datensatz')
    plt.ylabel('Normalisierte Häufigkeit')
    plt.xlabel('6-Gramme')
    plt.tick_params(
        axis='x',  # changes apply to the x-axis
        which='both',  # both major and minor ticks are affected
        bottom=False,  # ticks along the bottom edge are off
        top=False,  # ticks along the top edge are off
        labelbottom=False)  # labels along the bottom edge are off
    plt.show()
print_histogram()