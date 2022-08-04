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

HTTP_RE = re.compile(r"--START--.+?Hour: .+?\s+(.+?)\s+--END--", re.MULTILINE | re.DOTALL)


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
    for line in (req.strip()).splitlines():
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

def send_data(p: pipeline.Pipeline):
    time.sleep(5)

    script_dir = os.path.dirname(__file__)  # <-- absolute dir the script is in
    rel_path = "scans.txt"
    path_data = os.path.join(script_dir, rel_path)

    http_requests = get_requests_from_file(path_data)
    print(f"# of requests: {str(len(http_requests))}")
    #print(http_requests[500])
    #return

    my_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "de,en-US;q=0.7,en;q=0.3",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }

    try:
        print("Start sending requests")
        i = 1
        for req in http_requests:
            if i % 7 == 0:
                print(f"Request {i}")
                requests.get(url="http://127.0.0.1:80/web/admin.html", auth=("admin", "admin"), headers=my_headers)
                i = i + 1
            else:
                my_method, my_uri, my_header, dictRequest = _process_request(req)
                if my_method == 'GET':
                    print(f"Request {i}")
                    requests.get(url=my_uri, headers=my_header)
                    i = i + 1
                elif my_method == 'POST':
                    print(f"Request {i}")
                    if not 'body' in dictRequest:
                        dictRequest['body'] = ''
                        my_header['Content-Length'] = '0'
                    requests.post(url=my_uri, headers=my_header, data=dictRequest['body'])
                    i = i + 1
                elif my_method == 'PUT':
                    print(f"Request {i}")
                    requests.put(url=my_uri, headers=my_header, data=dictRequest['body'])
                    i = i + 1
    
    except Exception as e:
        print(f"UNEXPECTED ERROR: {e}")    
    finally:
        print("Finally")
        r = p.stage_typing.get_path_reliabilities()
        print(r)
        f = open("test/honeypotDataset/path_reliabilities.txt", "a")
        f.write(str(datetime.now()))
        f.write(", ")
        f.write(str(r))
        f.write("\n")
        f.close()
        print("Waiting until write queue is empty")
        p.database_handler.queue.join()
        os._exit(0)


if __name__ == '__main__':
    p = pipeline.Pipeline("", "test", True)
    t = threading.Thread(target=p.init_pipeline).start()
    send_data(p)
