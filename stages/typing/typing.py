from typing import List
from stages import Stage
from dtos import DTO, FilterTypingDTO
import sys
from abc import ABCMeta, abstractmethod
from pathlib import Path
from datetime import datetime


class Typing(Stage):
    def __init__(self, successor: 'Stage'):
        self.root = RootNode()
        super().__init__(successor)

    def run(self, dto: DTO) -> None:
        if not isinstance(dto, FilterTypingDTO):
            sys.exit("Typing: FilterTypingDTO required.")

        ts = datetime.now()
        self.root.add_timestamp(ts)
        
        path_list = list(Path(dto.message.path).parts)
        path_list.pop(0)
        print(path_list)
        self.root.add_child(path_list, dto.message.method)


class INode(metaclass=ABCMeta):
    def __init__(self) -> None:
        pass

    @abstractmethod
    def aggregate(self) -> None:
        pass

    @abstractmethod
    def add_timestamp(self, ts: datetime) -> None:
        pass
     

class RootNode(INode):
    def __init__(self) -> None:
        self.GET_nodes = []
        self.POST_nodes = []
        self.HEAD_nodes = []
        self.PUT_nodes = []
        self.DELETE_nodes = []
        self.OPTIONS_nodes = []
        self.PATCH_nodes = []

        self.core_node = True
        
        self.timestamps_short_term = []
        self.timestamps_medium_term = []
        self.timestamps_long_term = []

    def add_child(self, path_list: List, method: str) -> None:
        if len(path_list) < 2: # Resource
            if len(path_list) == 0: # Root
                res_name = "/"
            else:
                res_name = path_list[0]
            child = next((x for x in getattr(self, method+"_nodes") if (isinstance(x, ResourceNode) and x.name == res_name)), None)
            if child is None: # Resource doesn't exist yet
                child = ResourceNode(res_name)
                getattr(self, method+"_nodes").append(child)
            child.add_timestamp(self.timestamps_short_term[-1])
        else: # Directory
            dir_name = path_list[0]
            child = next((x for x in getattr(self, method+"_nodes") if (isinstance(x, DirNode) and x.name == dir_name)), None)
            if child is None: # Directory doesn't exist yet
                child = DirNode(dir_name)
                getattr(self, method+"_nodes").append(child)
            child.add_timestamp(self.timestamps_short_term[-1])
            path_list.pop(0)
            child.add_child(path_list)


    def add_timestamp(self, ts: datetime) -> None:
        self.timestamps_short_term.append(ts)
    
    def aggregate(self) -> None:
        pass


class DirNode(INode):
    def __init__(self, dir_name: str) -> None:
        self.name = dir_name
        
        self.children = []

        self.timestamps_short_term = []
        self.timestamps_medium_term = []
        self.timestamps_long_term = []

    def add_child(self, path_list: List) -> None:
        if len(path_list) == 1: # Resource
            res_name = path_list[0]
            child = next((x for x in self.children if (isinstance(x, ResourceNode) and x.name == res_name)), None)
            if child is None: # Resource doesn't exist yet
                child = ResourceNode(res_name)
                self.children.append(child)
            child.add_timestamp(self.timestamps_short_term[-1])
        else: # Directory
            dir_name = path_list[0]
            child = next((x for x in self.children if (isinstance(x, DirNode) and x.name == dir_name)), None)
            if child is None: # Directory doesn't exist yet
                child = DirNode(dir_name)
                self.children.append(child)
            child.add_timestamp(self.timestamps_short_term[-1])
            path_list.pop(0)
            child.add_child(path_list)

    def add_timestamp(self, ts: datetime) -> None:
        self.timestamps_short_term.append(ts)
    
    def aggregate(self) -> None:
        pass


class ResourceNode(INode):
    def __init__(self, resource_name: str) -> None:
        self.name = resource_name

        self.timestamps_short_term = []
        self.timestamps_medium_term = []
        self.timestamps_long_term = []

    def add_timestamp(self, ts: datetime) -> None:
        self.timestamps_short_term.append(ts)
    
    def aggregate(self) -> None:
        pass
