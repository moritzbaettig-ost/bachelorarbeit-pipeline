import os
import re
import requests

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


script_dir = os.path.dirname(__file__)  # <-- absolute dir the script is in
#rel_path = "vulnbank_train.txt"
rel_path = "vulnbank_anomaly.txt"
path_normal_data = os.path.join(script_dir, rel_path)

# path_anomaly_data = "vulnbank_anomaly.txt"

http_requests = get_requests_from_file(path_normal_data)
for req in http_requests:
    my_method, my_uri, my_header, dictRequest = _process_request(req)
    if my_method == 'GET':
        r = requests.get(url=my_uri, headers=my_header)
        print(r)
    elif my_method == 'POST':
        r = requests.post(url=my_uri, headers=my_header, data=dictRequest['body'])
        print(dictRequest['body'])
        print(r)
    elif my_method == 'PUT':
        r = requests.put(url=my_uri, headers=my_header, data=dictRequest['body'])
        print(dictRequest['body'])
        print(r)
