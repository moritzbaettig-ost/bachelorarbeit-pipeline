import requests
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
import urllib3
import urllib.parse as parser
from message import IDSHTTPMessage
from stages import Stage
from stages.filter import RequestFilter
from dtos import DTO, AcquisitionFilterDTO


class Acquisition(Stage):
    def __init__(self, successor: RequestFilter, hostname: str):
        self.hostname = hostname
        super().__init__(successor)


    def run(self, dto: DTO) -> None:
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        handler = ProxyHTTPRequestHandler(self.hostname, self.successor)
        server = ThreadedHTTPServer(('0.0.0.0', 80), handler)
        # server = HTTPServer(('0.0.0.0', 80), handler)
        server.serve_forever()


class ProxyHTTPRequestHandler(BaseHTTPRequestHandler):
    def __init__(self, hostname: str, successor: RequestFilter):
        self.protocol_version = 'HTTP/1.1'
        self.hostname = hostname
        self.successor = successor

    def __call__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def do_HEAD(self):
        self.do_GET(body=False)
        return

    def do_GET(self, body=True):
        self.process_request('GET', '')
        sent = False
        try:
            url = 'http://{}{}'.format(self.hostname, self.path)
            # print(url)
            req_header = self.parse_headers()

            # print(req_header)
            # print(self.headers)
            # print(url)
            resp = requests.get(url, headers=self.merge_two_dicts(req_header, self.set_header()), verify=False)
            sent = True

            self.send_response(resp.status_code)
            self.send_resp_headers(resp)
            msg = resp.text
            if body:
                self.wfile.write(msg.encode(encoding='UTF-8', errors='strict'))
            return
        finally:
            if not sent:
                self.send_error(404, 'error trying to proxy')

    def do_POST(self, body=True):
        content_len = int(self.headers.get('content-length'))
        post_body = self.rfile.read(content_len)
        self.process_request('POST', post_body)
        sent = False
        try:
            url = 'http://{}{}'.format(self.hostname, self.path)
            req_header = self.parse_headers()
            resp = requests.post(url, data=post_body, headers=self.merge_two_dicts(req_header, self.set_header()), verify=False)
            sent = True
            self.send_response(resp.status_code)
            self.send_resp_headers(resp)
            if body:
                self.wfile.write(resp.content)
            return
        finally:
            if not sent:
                self.send_error(404, 'error trying to proxy')

    def parse_headers(self):
        req_header = {}
        for attr in self.headers:
            req_header[attr] = self.headers[attr]
        return req_header

    def send_resp_headers(self, resp):
        respheaders = resp.headers
        # print('Response Header')
        for key in respheaders:
            if key not in ['Content-Encoding', 'Transfer-Encoding', 'content-encoding', 'transfer-encoding',
                           'content-length', 'Content-Length']:
                # print(key, respheaders[key])
                self.send_header(key, respheaders[key])
        self.send_header('Content-Length', str(len(resp.content)))
        self.end_headers()

    def log_message(self, format, *args):
        return

    def log_request(self, code='-', size='-'):
        return

    def merge_two_dicts(self, x, y):
        return x | y

    def set_header(self):
        headers = {
            'Host': self.hostname
        }
        return headers

    def process_request(self, req_type, post_body):
        path_query_split = self.path.split('?', 1)
        m = IDSHTTPMessage(
            source_address=self.client_address[0],
            method=req_type,
            path=path_query_split[0],
            query='',
            protocol_version=self.protocol_version,
            header=self.headers,
            body=post_body
        )
        if len(path_query_split) == 2:
            m.query = parser.unquote(path_query_split[1])
        if req_type == 'POST':
            m.body = m.body.decode('utf-8')
            m.body=parser.unquote(m.body)
        print(m)
        dto = AcquisitionFilterDTO(message=m)
        self.successor.run(dto)



class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""
