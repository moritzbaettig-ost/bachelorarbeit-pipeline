import sys
import pathlib
directory = pathlib.Path(__file__).resolve()
sys.path.append(directory.parent.parent)
print(sys.path)
from stages.typing import Typing
from message import IDSHTTPMessage
from dtos import FilterTypingDTO


if __name__ == '__main__':
    typing_stage = Typing(None)
    test_message = IDSHTTPMessage(
        source_address="99.99.99.99",
        method="GET",
        path="/dir1/dir2/res.jpg",
        query="key1=val1&key2=val2",
        protocol_version="HTTP 1.1",
        header=None,
        body=""
    )
    test_dto = FilterTypingDTO(message=test_message)
