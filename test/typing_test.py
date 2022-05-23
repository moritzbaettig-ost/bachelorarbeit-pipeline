import sys
import pathlib
from time import sleep
directory = pathlib.Path(__file__)
sys.path.append(directory.parent.parent.__str__())
from stages.typing import Typing
from stages.extraction import Extraction
from message import IDSHTTPMessage
from dtos import FilterTypingDTO


if __name__ == '__main__':
    stage_extraction = Extraction(None)
    typing_stage = Typing(stage_extraction)
    sleep(1)
    test_message = IDSHTTPMessage(
        source_address="99.99.99.99",
        method="GET",
        path="  ",
        query="key1=val1&key2=val2",
        protocol_version="HTTP 1.1",
        header=None,
        body=""
    )
    test_dto = FilterTypingDTO(message=test_message)
    
    test_dto.message.path = "/"
    typing_stage.run(test_dto)
    typing_stage.run(test_dto)

    test_dto.message.path = "/index.html"
    typing_stage.run(test_dto)
    sleep(0.5)
    typing_stage.run(test_dto)
    typing_stage.run(test_dto)
    typing_stage.run(test_dto)

    test_dto.message.path = "/test/index.html"
    typing_stage.run(test_dto)
    #print("\n---- START TREE ----\n")
    #print(typing_stage.root)
    #print("\n---- END TREE ----\n")
