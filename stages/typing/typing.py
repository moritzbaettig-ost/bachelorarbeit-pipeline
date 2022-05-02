from stages import Stage
from dtos import DTO, FilterTypingDTO
import sys


class Typing(Stage):
    def __init__(self, successor: 'Stage'):
        super().__init__(successor)

    def run(self, dto: DTO) -> None:
        if not isinstance(dto, FilterTypingDTO):
            sys.exit("Typing: FilterTypingDTO required.")
        print(dto.message)


class RootNode:
    pass


class DirNode:
    pass


class ResourceNode:
    pass
