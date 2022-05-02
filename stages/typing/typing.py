from stages import Stage
from dtos import DTO, FilterTypingDTO
import sys
from typing import Union


class Typing(Stage):
    def __init__(self, successor: 'Stage'):
        super().__init__(successor)

    def run(self, dto: DTO) -> None:
        if not isinstance(dto, FilterTypingDTO):
            sys.exit("Typing: FilterTypingDTO required.")
        print(dto.message)


class RootNode:
    def __init__(self, method: str) -> None:
        self.method = method
        self.children = []

    def add_child(self, child: 'DirNode') -> None:
        self.children.append(child)


class DirNode:
    def __init__(self, dir_name: str) -> None:
        self.dir_name = dir_name
        self.children = []

    def add_child(self, child: Union['DirNode', 'ResourceNode']) -> None:
        self.children.append(child)


class ResourceNode:
    def __init__(self, resource_name: str) -> None:
        self.resource_name = resource_name
