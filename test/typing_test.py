import sys
import pathlib
from time import sleep
directory = pathlib.Path(__file__)
sys.path.append(directory.parent.parent.__str__())
from stages.typing import Typing
from message import IDSHTTPMessage
from dtos import FilterTypingDTO


if __name__ == '__main__':
    typing_stage = Typing(None)
    sleep(1)
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
    typing_stage.run(test_dto)
    #typing_stage.run(test_dto)
    test_dto.message.path = "/index.html"
    sleep(3)
    typing_stage.run(test_dto)
    #typing_stage.run(test_dto)
    print(typing_stage.root)
