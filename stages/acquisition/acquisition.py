import requests
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
import urllib3
import urllib.parse as parser
from message import IDSHTTPMessage
from stages import Stage
from dtos import DTO, AcquisitionFilterDTO


class Acquisition(Stage):
    """
    A class that represents the first stage of the ML-IDS pipeline.
    This stage acquires HTTP requests by setting up a simple HTTP reverse proxy server.

    Attributes
    ----------
    successor: Stage
        The stage that follows this stage in the pipeline.
    hostname: str
        The hostname of the service that the IDS has to secure.

    Methods
    ----------
    run(successor, hostname)
        The method that gets called by the previous stage.
    """

    def __init__(self, successor: Stage, hostname: str):
        """
        Parameters
        ----------
        successor: Stage
            The stage that follows this stage in the pipeline.
        hostname: str
            The hostname of the service that the IDS has to secure.
        """

        self.successor = successor
        self.hostname = hostname


    def run(self, dto: DTO) -> None:
        """
        The method that gets called by the previous stage.

        Parameters
        ----------
        dto : DTO
            The data transer object that is received from the previous stage.
        """

        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        handler = ProxyHTTPRequestHandler(self.hostname, self.successor)
        server = ThreadedHTTPServer(('0.0.0.0', 80), handler)
        # server = HTTPServer(('0.0.0.0', 80), handler)
        server.serve_forever()


class ProxyHTTPRequestHandler(BaseHTTPRequestHandler):
    """
    This class represents the handler that processes all HTTP requests.

    Attributes
    ----------
    protocol_version : str
        The version of the HTTP protocol.
    hostname: str
        The hostname of the service that the IDS has to secure.
    successor: Stage
        The stage that follows this stage in the pipeline.

    Methods
    ----------
    do_HEAD()
        Processes all the HEAD-requests.
    do_GET(body=True)
        Processes all the GET-requests.
    do_POST(body=True)
        Processes all the POST-requests.
    parse_headers()
        Parses the HTTP headers for the request to the service.
    send_resp_headers(resp)
        Sends the response headers to the client that made the request.
    log_message(format, *args)
        Logs a HTTP message.
    log_request(code='-', size='-')
        Logs a HTTP request.
    merge_two_dicts(x, y)
        Merges two dictionaries to one new dictionary.
    set_header()
        Sets the hostname of the secured service in the HTTP header.
    process_request(req_type, post_body)
        Processes the gathered HTTP request by creating a IDSHTTPMessage object and passing it to the next stage in the pipeline.
    """

    def __init__(self, hostname: str, successor: Stage):
        """
        Parameters
        ----------
        hostname : str
            The hostname of the service that the IDS has to secure.
        successor: Stage
            The stage that follows this stage in the pipeline.
        """

        self.protocol_version = 'HTTP/1.1'
        self.hostname = hostname
        self.successor = successor

    def __call__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def do_HEAD(self):
        """
        Processes all the HEAD-requests.
        """

        self.do_GET(body=False)
        return

    def do_GET(self, body=True):
        """
        Processes all the GET-requests.

        Parameters
        ----------
        body : bool
            States if the response has a body. 
        """

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
        """
        Processes all the POST-requests.

        Parameters
        ----------
        body : bool
            States if the response has a body. 
        """
        
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
        """
        Parses the HTTP headers for the request to the service.
        """

        req_header = {}
        for attr in self.headers:
            req_header[attr] = self.headers[attr]
        return req_header

    def send_resp_headers(self, resp):
        """
        Sends the response headers to the client that made the request.

        Parameters
        ----------
        resp : HTTPMessage
            The HTTP response that has to be sent back to the original client.
        """

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
        """
        Logs a HTTP message.

        This method overwrites the method in the parent class and surpresses the message log so the console is not spammed.
        """

        return

    def log_request(self, code='-', size='-'):
        """
        Logs a HTTP request.

        This method overwrites the method in the parent class and surpresses the request log so the console is not spammed.
        """

        return

    def merge_two_dicts(self, x, y):
        """
        Merges two dictionaries to one new dictionary.
        
        Parameters
        ----------
        x : dict
            First dictionary
        y : dict
            Second dictionary

        Returns
        ----------
        dict
            Merged dictionary
        """

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
