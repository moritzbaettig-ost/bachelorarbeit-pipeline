import requests
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
import urllib3
import io

_hostname = None
_successor = None


def start_proxy(successor, hostname):
    global _hostname
    _hostname = hostname
    proxy_address = ('0.0.0.0', 80)
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    httpd = ThreadedHTTPServer(proxy_address, ProxyHTTPRequestHandler)
    httpd.serve_forever()

    global _successor
    _successor = successor


def merge_two_dicts(x, y):
    return x | y


def set_header():
    headers = {
        'Host': _hostname
    }
    return headers


def process_request(req, req_type):
    final_string = ""
    final_string += "Source Address: " + req.client_address[0]
    final_string += "\n"
    final_string += req_type + " " + req.path + " " + req.protocol_version
    final_string += "\n"
    final_string += req.headers
    if req_type == 'POST':
        l = int(req.headers['Content-Length'])
        post_data = req.rfile.read(l)
        final_string += "\n"
        final_string += post_data.decode('utf-8')
    _successor.filter_request(final_string)


class ProxyHTTPRequestHandler(BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.1'

    def do_HEAD(self):
        self.do_GET(body=False)
        return

    def do_GET(self, body=True):
        process_request(self, 'GET')
        sent = False
        try:
            url = 'http://{}{}'.format(_hostname, self.path)
            # print(url)
            req_header = self.parse_headers()

            # print(req_header)
            # print(self.headers)
            # print(url)
            resp = requests.get(url, headers=merge_two_dicts(req_header, set_header()), verify=False)
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
        process_request(self, 'POST')
        sent = False
        try:
            url = 'http://{}{}'.format(_hostname, self.path)
            content_len = int(self.headers.get('content-length'))
            post_body = self.rfile.read(content_len)
            req_header = self.parse_headers()

            resp = requests.post(url, data=post_body, headers=merge_two_dicts(req_header, set_header()), verify=False)
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
        for line in self.headers:
            line_parts = [o.strip() for o in line.split(':', 1)]
            if len(line_parts) == 2:
                req_header[line_parts[0]] = line_parts[1]
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


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""
