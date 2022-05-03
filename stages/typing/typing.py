from stages import Stage
from dtos import DTO, FilterTypingDTO
import sys
from typing import Union
from abc import ABCMeta, abstractmethod
from pathlib import Path


class Typing(Stage):
    def __init__(self, successor: 'Stage'):
        super().__init__(successor)

    def run(self, dto: DTO) -> None:
        if not isinstance(dto, FilterTypingDTO):
            sys.exit("Typing: FilterTypingDTO required.")
        root = RootNode()
        # print(Path(dto.message.path).parts)


class INode(metaclass=ABCMeta):
    def __init__(self) -> None:
        pass

    @property
    @abstractmethod
    def timestamps_short_term(self):
        pass

    @property
    @abstractmethod
    def timestamps_medium_term(self):
        pass

    @property
    @abstractmethod
    def timestamps_long_term(self):
        pass


    @property
    @abstractmethod
    def core_node(self):
        pass


    @abstractmethod
    def aggregate(self) -> None:
        pass
     

class RootNode(INode):
    def __init__(self) -> None:
        self.GET_nodes = []
        self.POST_nodes = []
        self.HEAD_nodes = []
        self.PUT_nodes = []
        self.DELETE_nodes = []
        self.CONNECT_nodes = []
        self.OPTIONS_nodes = []
        self.TRACE_nodes = []
        self.PATCH_nodes = []

        self.core_node = True

    def add_child(self, child: 'DirNode') -> None:
        self.children.append(child)


class DirNode(INode):
    def __init__(self, dir_name: str) -> None:
        self.dir_name = dir_name
        self.children = []

    def add_child(self, child: Union['DirNode', 'ResourceNode']) -> None:
        self.children.append(child)


class ResourceNode(INode):
    def __init__(self, resource_name: str) -> None:
        self.resource_name = resource_name
