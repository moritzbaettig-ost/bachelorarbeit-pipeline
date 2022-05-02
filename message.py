from dataclasses import dataclass
from http.client import HTTPMessage


@dataclass
class IDSHTTPMessage:
    source_address: str
    method: str
    path: str
    query: str
    protocol_version: str
    header: HTTPMessage
    body: str
    
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