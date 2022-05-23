from typing import List
from stages import Stage
from dtos import DTO, FilterTypingDTO, TypingExtractionDTO
import sys
from abc import ABCMeta, abstractmethod
from pathlib import Path
from datetime import datetime
import json
import os
import textwrap
import copy
from type import Type


class Typing(Stage):
    def __init__(self, successor: 'Stage'):
        self.root = RootNode(datetime.now())
        self.init_core()
        super().__init__(successor)

    def init_core(self):
        here = os.path.dirname(os.path.abspath(__file__))
        filename = os.path.join(here, 'config.json')
        data = json.load(open(filename))
        for path in data['paths']:
            path_list = list(Path(path['path']).parts)
            path_list.pop(0)
            for method in path['methods']:
                temp_path_list = copy.deepcopy(path_list)
                self.root.add_child(temp_path_list, method, True)
        self.root.update_reliability()

    def run(self, dto: DTO) -> None:
        if not isinstance(dto, FilterTypingDTO):
            sys.exit("Typing: FilterTypingDTO required.")

        # Expand Tree
        ts = datetime.now()
        self.root.add_timestamp(ts)
        
        path_list = list(Path(dto.message.path).parts)
        path_list.pop(0)
        dir_node = self.root.add_child(path_list, dto.message.method, False)
        self.root.update_reliability()
        path_reliability = dir_node.path_reliability
        # TODO: Throw alert if Path Reliability is under specific value

        # Typing
        t = Type(dto.message.method, dto.message.path, dto.message.query != '', dto.message.body != '')

        new_dto = TypingExtractionDTO(dto.message, t)

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
    def __init__(self, init_time: datetime) -> None:
        self.GET_nodes = []
        self.POST_nodes = []
        self.HEAD_nodes = []
        self.PUT_nodes = []
        self.DELETE_nodes = []
        self.OPTIONS_nodes = []
        self.PATCH_nodes = []

        self.core_node = True

        self.init_time = init_time
        
        self.timestamps_short_term = []
        self.timestamps_medium_term = []
        self.timestamps_long_term = []

    def add_child(self, path_list: List, method: str, core: bool) -> INode:
        if len(path_list) < 2: # Resource
            if len(path_list) == 0: # Root
                res_name = "/"
            else:
                res_name = path_list[0]
            child = next((x for x in getattr(self, method+"_nodes") if (isinstance(x, ResourceNode) and x.name == res_name)), None)
            if child is None: # Resource doesn't exist yet
                child = ResourceNode(res_name)
                if not core:
                    child.init_time = self.timestamps_short_term[-1]
                else:
                    child.core_node = True
                    child.reliability = 1.0
                    child.path_reliability = 1.0
                    child.init_time = self.init_time
                getattr(self, method+"_nodes").append(child)
            if not core:
                child.add_timestamp(self.timestamps_short_term[-1])
            reference = child
        else: # Directory
            dir_name = path_list[0]
            child = next((x for x in getattr(self, method+"_nodes") if (isinstance(x, DirNode) and x.name == dir_name)), None)
            if child is None: # Directory doesn't exist yet
                child = DirNode(dir_name)
                if not core:
                    child.init_time = self.timestamps_short_term[-1]
                else:
                    child.core_node = True
                    child.reliability = 1.0
                    child.init_time = self.init_time
                getattr(self, method+"_nodes").append(child)
            if not core:
                child.add_timestamp(self.timestamps_short_term[-1])
            path_list.pop(0)
            reference = child.add_child(path_list, core)
        return reference


    def add_timestamp(self, ts: datetime) -> None:
        self.timestamps_short_term.append(ts)
    
    def aggregate(self) -> None:
        pass

    def update_reliability(self) -> None:
        for c in self.GET_nodes:
            c.update_reliability(len(self.timestamps_short_term), 1.0)
        for c in self.POST_nodes:
            c.update_reliability(len(self.timestamps_short_term), 1.0)
        for c in self.HEAD_nodes:
            c.update_reliability(len(self.timestamps_short_term), 1.0)
        for c in self.PUT_nodes:
            c.update_reliability(len(self.timestamps_short_term), 1.0)
        for c in self.DELETE_nodes:
            c.update_reliability(len(self.timestamps_short_term), 1.0)
        for c in self.OPTIONS_nodes:
            c.update_reliability(len(self.timestamps_short_term), 1.0)
        for c in self.PATCH_nodes:
            c.update_reliability(len(self.timestamps_short_term), 1.0)

    def __str__(self):
        return f"---- ROOT Node ----\n" \
            f"Core: {self.core_node}\n" \
            f"Initial Time: {self.init_time}\n" \
            f"# of Timestamps Short Term: {len(self.timestamps_short_term)}\n" \
            f"Timestamps Short Term: {self.timestamps_short_term}\n" \
            f"GET Nodes: {self.GET_nodes}\n" \
            f"POST Nodes: {self.POST_nodes}\n" \
            "---- End ROOT ----"


class DirNode(INode):
    def __init__(self, dir_name: str) -> None:
        self.name = dir_name
        
        self.children = []

        self.init_time = None

        self.timestamps_short_term = []
        self.timestamps_medium_term = []
        self.timestamps_long_term = []

        self.core_node = False

        self.reliability = 0.0

    def add_child(self, path_list: List, core: bool) -> INode:
        if len(path_list) == 1: # Resource
            res_name = path_list[0]
            child = next((x for x in self.children if (isinstance(x, ResourceNode) and x.name == res_name)), None)
            if child is None: # Resource doesn't exist yet
                child = ResourceNode(res_name)
                if not core:
                    child.init_time = self.timestamps_short_term[-1]
                else:
                    child.core_node = True
                    child.reliability = 1.0
                    child.path_reliability = 1.0
                    child.init_time = self.init_time
                self.children.append(child)
            if not core:
                child.add_timestamp(self.timestamps_short_term[-1])
            reference = child
        else: # Directory
            dir_name = path_list[0]
            child = next((x for x in self.children if (isinstance(x, DirNode) and x.name == dir_name)), None)
            if child is None: # Directory doesn't exist yet
                child = DirNode(dir_name)
                if not core:
                    child.init_time = self.timestamps_short_term[-1]
                else:
                    child.core_node = True
                    child.reliability = 1.0
                    child.init_time = self.init_time
                self.children.append(child)
            if not core:
                child.add_timestamp(self.timestamps_short_term[-1])
            path_list.pop(0)
            reference = child.add_child(path_list, core)
        return reference

    def add_timestamp(self, ts: datetime) -> None:
        self.timestamps_short_term.append(ts)
    
    def aggregate(self) -> None:
        pass

    def update_reliability(self, parent_length: float, calculated_reliability: float) -> None:
        if not self.core_node:
            self.reliability = len(self.timestamps_short_term) / parent_length
        for c in self.children:
            c.update_reliability(len(self.timestamps_short_term), calculated_reliability*self.reliability)
    
    def __str__(self):
        return f"---- DIR Node: {self.name} ----\n" \
            f"Core: {self.core_node}\n" \
            f"Initial Time: {self.init_time}\n" \
            f"# of Timestamps Short Term: {len(self.timestamps_short_term)}\n" \
            f"Timestamps Short Term: {self.timestamps_short_term}\n" \
            f"Reliability: {self.reliability}\n" \
            f"Children: {self.children}\n" \
            f"---- End Dir: {self.name} ----"

    def __repr__(self):
        return textwrap.indent(f"\n{self.__str__()}\n", 4 * ' ')


class ResourceNode(INode):
    def __init__(self, resource_name: str) -> None:
        self.name = resource_name

        self.init_time = None

        self.timestamps_short_term = []
        self.timestamps_medium_term = []
        self.timestamps_long_term = []

        self.core_node = False

        self.reliability = 0.0
        self.path_reliability = 0.0

    def add_timestamp(self, ts: datetime) -> None:
        self.timestamps_short_term.append(ts)
    
    def aggregate(self) -> None:
        pass

    def update_reliability(self, parent_length: float, calculated_reliability: float) -> None:
        if not self.core_node:
            self.reliability = len(self.timestamps_short_term) / parent_length
            self.path_reliability = calculated_reliability * self.reliability

    def __str__(self):
        return f"---- RES Node: {self.name} ----\n" \
            f"Core: {self.core_node}\n" \
            f"Initial Time: {self.init_time}\n" \
            f"# of Timestamps Short Term: {len(self.timestamps_short_term)}\n" \
            f"Timestamps Short Term: {self.timestamps_short_term}\n" \
            f"Reliability: {self.reliability}\n" \
            f"Path Reliability: {self.path_reliability}\n" \
            f"---- End RES: {self.name} ----"

    def __repr__(self):
        return textwrap.indent(f"\n{self.__str__()}\n", 4 * ' ')
