from stages import Stage
from dtos import DTO, TypingExtractionDTO
import sys

class Extraction(Stage):
    def __init__(self, successor: 'Stage'):
        super().__init__(successor)

    def run(self, dto: DTO) -> None:
        if not isinstance(dto, TypingExtractionDTO):
            sys.exit("Typing: FilterTypingDTO required.")
        # TODO: Extraction Stage based on type
        #print(dto.message)
