import pathlib
import sys
directory = pathlib.Path(__file__)
sys.path.append(directory.parent.parent.parent.__str__())

import os
import re
import requests
import pipeline
import threading
import time
import ZODB, ZODB.FileStorage, ZODB.DB
from datetime import datetime

HTTP_RE = re.compile(r"(.+?)\s\n\n", re.MULTILINE | re.DOTALL)
HTTP_RE2 = re.compile(r"(.+?)\n\n(.+?)\n\n", re.MULTILINE | re.DOTALL)


def http_re(data):
    """
    Extracts HTTP requests from raw data string in special logging format.
    Logging format `ST@RT\n%(asctime)s %(levelname)-8s\n%(message)s\nEND`
    where `message` is a required HTTP request bytes.
    """

    tmp_requests = HTTP_RE.findall(data)
    requests=[]
    for i in range(len(tmp_requests)):
        tmp=HTTP_RE2.findall(tmp_requests[i])
        if len(tmp)>0:
            for j in range(len(tmp)):
                temp_str=tmp[j][0]+"\n\n"+tmp[j][1]+"\n"
                requests.append(temp_str)
        else:
            requests.append(tmp_requests[i])
    return requests


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
            if line.split()[1].split('localhost:8080')[1].startswith('/') or line.split()[1].split('localhost:8080')[1].startswith('?'):
                my_uri = my_uri + line.split()[1].split('localhost:8080')[1]
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


def send_data(p: pipeline.Pipeline):
    time.sleep(5)

    script_dir = os.path.dirname(__file__)  # <-- absolute dir the script is in
    rel_path_train = "http_normal.txt"
    rel_path_anomaly = "http_anomaly.txt"
    path_normal_data = os.path.join(script_dir, rel_path_train)
    path_anomaly_data = os.path.join(script_dir, rel_path_anomaly)

    http_requests_normal = get_requests_from_file(path_normal_data)
    http_requests_anomaly = get_requests_from_file(path_anomaly_data)
    print(f"# of anomaly requests: {str(len(http_requests_anomaly))}")
    print(f"# of normal requests: {str(len(http_requests_normal))}")

    """
    for req in http_requests_anomaly:
        my_method, my_uri, my_header, dictRequest = _process_request(req)
        print(my_method)
        print(my_uri)
        print(my_header)
        print(dictRequest)

    for req in http_requests_normal:
        my_method, my_uri, my_header, dictRequest = _process_request(req)
        print(my_method)
        print(my_uri)
        print(my_header)
        print(dictRequest)
    """

    try:
        print("Start sending anomaly requests")
        i = 1
        p.stage_extraction.label = 1
        for req in http_requests_anomaly:
            my_method, my_uri, my_header, dictRequest = _process_request(req)
            if my_method == 'GET':
                print(f"Anomaly Request {i}")
                requests.get(url=my_uri, headers=my_header)
                i = i + 1
            elif my_method == 'POST':
                print(f"Anomaly Request {i}")
                requests.post(url=my_uri, headers=my_header, data=dictRequest['body'])
                i = i + 1
            elif my_method == 'PUT':
                print(f"Anomaly Request {i}")
                requests.put(url=my_uri, headers=my_header, data=dictRequest['body'])
                i = i + 1
        print("Start sending normal requests")
        i = 1
        p.stage_extraction.label = 0
        for req in http_requests_normal:
            my_method, my_uri, my_header, dictRequest = _process_request(req)
            if my_method == 'GET':
                print(f"Normal Request {i}")
                requests.get(url=my_uri, headers=my_header)
                i = i + 1
            elif my_method == 'POST':
                print(f"Normal Request {i}")
                requests.post(url=my_uri, headers=my_header, data=dictRequest['body'])
                i = i + 1
            elif my_method == 'PUT':
                print(f"Normal Request {i}")
                requests.put(url=my_uri, headers=my_header, data=dictRequest['body'])
                i = i + 1
    except Exception as e:
        print(f"UNEXPECTED ERROR: {e}")
    finally:
        print("Finally")
        r = p.stage_typing.get_path_reliabilities()
        print(r)
        f = open("test/httpDataset/path_reliabilities.txt", "a")
        f.write(str(datetime.now()))
        f.write(", ")
        f.write(str(r))
        f.write("\n")
        f.close()
        print("Waiting until write queue is empty")
        p.database_handler.queue.join()
        os._exit(0)


if __name__ == '__main__':
    p = pipeline.Pipeline("146.136.47.202", "train", False)
    t = threading.Thread(target=p.init_pipeline).start()
    send_data(p)
