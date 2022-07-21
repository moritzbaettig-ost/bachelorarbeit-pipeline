from dataclasses import dataclass
from http.client import HTTPMessage


@dataclass
class IDSHTTPMessage:
    """
    This class represents a HTTP message that is passed inside of the IDS-Pipeline.

    Attributes
    ----------
    source_address: str
        The source IP-address of the HTTP request.
    method: str
        The HTTP method that is used (GET, POST, ...)
    path: str
        The path on which the request is made
    query: str
        The query included in the request URL
    protocol_version: str
        The HTTP protocol version used
    header: HTTPMessage
        The HTTP headers
    body: str
        The HTTP body
    """
    
    source_address: str
    method: str
    path: str
    query: str
    protocol_version: str
    header: HTTPMessage
    body: str

    def string_for_prcessing(self):
        tmp = ''
        if self.query != '':
            tmp = '?'
        s = f"{self.method} {self.path}{tmp}{self.query} {self.protocol_version}\n" \
            f"{str(self.header)}\n" \
            f"{self.body}"
        return s
    
    def __str__(self):
        tmp = ''
        if self.query != '':
            tmp = '?'
        s = "---- HTTP Message ----\n" \
            f"Source Address: {self.source_address}\n" \
            f"{self.method} {self.path}{tmp}{self.query} {self.protocol_version}\n" \
            f"{str(self.header)}\n" \
            f"{self.body}"
        return s

    def __len__(self):
        return len(self.string_for_prcessing())