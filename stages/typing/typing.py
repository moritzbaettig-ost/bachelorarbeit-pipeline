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
from alerting.IObservable import IObservable
from alerting.IObserver import IObserver
from alerting.alert import Alert


class Typing(Stage, IObservable):
    """
    This class represents the third stage of the ML-IDS pipeline.
    This stage specifies the type the HTTP request and throws an alert if the path that is requested is unreliable.

    Attributes
    ----------
    successor: Stage
        The stage that follows this stage in the pipeline.
    root: RootNode
        The root of the typing tree.
    observers: list[IObserver]
        The list of the registered observers.

    Methods
    ----------
    run(dto)
        The method that gets called by the previous stage.
    init_core()
        Initializes the typing tree.
    get_path_reliabilities()
        Returns all the existing path reliabilies in the typing tree for analytics purposes.
    attach(observer)
        Attaches an observer to the observable.
    detach(observer)
        Detaches an observer from the observable.
    notify(alert)
        Notify all observers about an alert.    
    """

    def __init__(self, successor: 'Stage') -> None:
        """
        Parameters
        ----------
        successor: Stage
            The stage that follows this stage in the pipeline.
        """

        self.successor = successor
        self.root = RootNode(datetime.now())
        self.init_core()
        self._observers = []


    def init_core(self) -> None:
        """
        Initializes the typing tree.
        """

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


    def get_path_reliabilities(self) -> list:
        """
        Returns all the existing path reliabilies in the typing tree for analytics purposes.

        Returns
        ----------
        list
            All existing path reliabilities in the typing tree
        """

        path_reliabilities = []
        for node in self.root.GET_nodes:
            self._get_path_reliability_rec(node, path_reliabilities)
        for node in self.root.POST_nodes:
            self._get_path_reliability_rec(node, path_reliabilities)
        for node in self.root.HEAD_nodes:
            self._get_path_reliability_rec(node, path_reliabilities)
        for node in self.root.PUT_nodes:
            self._get_path_reliability_rec(node, path_reliabilities)
        for node in self.root.DELETE_nodes:
            self._get_path_reliability_rec(node, path_reliabilities)
        for node in self.root.OPTIONS_nodes:
            self._get_path_reliability_rec(node, path_reliabilities)
        for node in self.root.PATCH_nodes:
            self._get_path_reliability_rec(node, path_reliabilities)
        return path_reliabilities

    
    def _get_path_reliability_rec(self, node: 'INode', path_reliabilities: list) -> float:
        if isinstance(node, ResourceNode):
            path_reliabilities.append((node.name, node.path_reliability))
        elif isinstance(node, DirNode):
            for child_node in node.children:
                self._get_path_reliability_rec(child_node, path_reliabilities)


    def run(self, dto: DTO) -> None:
        """
        The method that gets called by the previous stage.

        Parameters
        ----------
        dto: DTO
            The data transfer object that is received from the previous stage.
        """

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
        RELIABILITY_THRESHOLD = 0.0
        #print(path_reliability)
        if path_reliability < RELIABILITY_THRESHOLD:
            alert = Alert(msg=f"Path unreliable ({path_reliability})", source="Typing Stage")
            self.notify(alert)
            return

        # Typing
        t = Type(dto.message.method, dto.message.path, dto.message.query != '', dto.message.body != '')

        new_dto = TypingExtractionDTO(dto.message, t)
        self.successor.run(new_dto)


    def attach(self, observer: IObserver) -> None:
        """
        Attaches an observer to the observable.

        Parameters
        ----------
        observer : IObserver
            The observer to attach.
        """

        self._observers.append(observer)


    def detach(self, observer: IObserver) -> None:
        """
        Detaches an observer from the observable.

        Parameters
        ----------
        observer : IObserver
            The observer to detach.
        """

        self._observers.remove(observer)


    def notify(self, alert: Alert) -> None:
        """
        Notify all observers about an alert.

        Parameters
        ----------
        alert: Alert
            The alert being the reason for the notification.
        """

        for observer in self._observers:
            observer.update(self, alert)


class INode(metaclass=ABCMeta):
    """
    This interface defines the default functions for all tree nodes.

    Methods
    ----------
    aggregate(ts)
        Aggregates the tracked timestamps:
        - All timestamps older than 1h are aggregated in the window of the last 24h in 1h steps.
        - All timestamps older than 24h are aggregated in the window of the last 7d in 1d steps.
        - All timestamps older than 7d are deleted.
    add_timestamp(ts)
        Adds a timestamp to the list.
    """

    @abstractmethod
    def aggregate(self, ts: datetime) -> None:
        """
        Aggregates the tracked timestamps:
        - All timestamps older than 1h are aggregated in the window of the last 24h in 1h steps.
        - All timestamps older than 24h are aggregated in the window of the last 7d in 1d steps.
        - All timestamps older than 7d are deleted.

        Parameters
        ----------
        ts: datetime
            The timestamp that just was added and is used as a reference.
        """

        pass


    @abstractmethod
    def add_timestamp(self, ts: datetime) -> None:
        """
        Adds a timestamp to the list.

        Parameters
        ----------
        ts: datetime
            The timestamp to add.
        """

        pass


class RootNode(INode):
    """
    This class represents the root node of the typing tree.

    Attributes
    ----------
    GET_nodes: list
        The nodes that are generated by a GET request.
    POST_nodes: list
        The nodes that are generated by a POST request.
    HEAD_nodes: list
        The nodes that are generated by a HEAD request.
    PUT_nodes: list
        The nodes that are generated by a PUT request.
    DELETE_nodes: list
        The nodes that are generated by a DELETE request.
    OPTIONS_nodes: list
        The nodes that are generated by a OPTIONS request.
    PATCH_nodes: list
        The nodes that are generated by a PATCH request.
    core_node: bool
        States if the node is a core node or not.
    init_time: datetime
        The timestamp of the time when the node was created.
    timestamps_short_term: list
        The list of the shortterm timestamps.
    timestamps_medium_term: list
        The list of the medium term timestamps.
    timestamps_long_term: list
        The list of the long term timestamps.

    Methods
    ----------
    add_child(path_list, method, core)
        Adds a child node to the current node.
    add_timestamp(ts)
        Adds a timestamp to the list.
    aggregate(ts)
        Aggregates the tracked timestamps:
        - All timestamps older than 1h are aggregated in the window of the last 24h in 1h steps.
        - All timestamps older than 24h are aggregated in the window of the last 7d in 1d steps.
        - All timestamps older than 7d are deleted.
    update_reliability()
        Calls the update_reliability method of all children with the needed paramteres.
    """

    def __init__(self, init_time: datetime) -> None:
        """
        Parameters
        ----------
        init_time: datetime
            The timestamp of the time when the node was created.
        """

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
        """
        Adds a child node to the current node.

        Parameters
        ----------
        path_list: list
            The list of the remaining path tokens of the request path.
        method: str
            The HTTP method of the request.
        core: bool
            If the node is a core node or not.

        Returns
        ----------
        INode
            The reference of the Resource Node of this specific path.
        """

        if len(path_list) < 2:  # Resource
            if len(path_list) == 0:  # Root
                res_name = "/"
            else:
                res_name = path_list[0]
            child = next(
                (x for x in getattr(self, method + "_nodes") if (isinstance(x, ResourceNode) and x.name == res_name)),
                None)
            if child is None:  # Resource doesn't exist yet
                child = ResourceNode(res_name)
                if not core:
                    child.init_time = self.timestamps_short_term[-1]
                else:
                    child.core_node = True
                    child.reliability = 1.0
                    child.path_reliability = 1.0
                    child.init_time = self.init_time
                getattr(self, method + "_nodes").append(child)
            if not core:
                child.add_timestamp(self.timestamps_short_term[-1])
            reference = child
        else:  # Directory
            dir_name = path_list[0]
            child = next(
                (x for x in getattr(self, method + "_nodes") if (isinstance(x, DirNode) and x.name == dir_name)), None)
            if child is None:  # Directory doesn't exist yet
                child = DirNode(dir_name)
                if not core:
                    child.init_time = self.timestamps_short_term[-1]
                else:
                    child.core_node = True
                    child.reliability = 1.0
                    child.init_time = self.init_time
                getattr(self, method + "_nodes").append(child)
            if not core:
                child.add_timestamp(self.timestamps_short_term[-1])
            path_list.pop(0)
            reference = child.add_child(path_list, core)
        return reference


    def add_timestamp(self, ts: datetime) -> None:
        """
        Adds a timestamp to the list.

        Parameters
        ----------
        ts: datetime
            The timestamp to be added.
        """

        self.timestamps_short_term.append(ts)
        self.aggregate(ts)


    def aggregate(self, ts: datetime) -> None:
        """
        Aggregates the tracked timestamps:
        - All timestamps older than 1h are aggregated in the window of the last 24h in 1h steps.
        - All timestamps older than 24h are aggregated in the window of the last 7d in 1d steps.
        - All timestamps older than 7d are deleted.

        Parameters
        ----------
        ts: datetime
            The timestamp that just was added and is used as a reference.
        """

        # Set the short term aggregation time in seconds (Should be 3600)
        short_term_aggregation = 5.0
        # Set the medium term aggregation time in seconds (Should be 86400)
        medium_term_aggregation = 20.0
        # Set the long term aggregation time in seconds (Should be 604800)
        long_term_aggregation = 100.0

        # Start short term aggregation
        for t in self.timestamps_short_term:
            # Time difference between entry and current time in seconds
            sec = abs((ts - t).total_seconds())
            # Check if short term entry needs to be aggregated
            if sec > short_term_aggregation:
                # Check if medium term list is not empty
                if len(self.timestamps_medium_term) > 0:
                    # Get the last timestamp from the medium term list
                    last_key = self.timestamps_medium_term[-1][0]
                    # Check if a new timestamp needs to be added to the medium term list
                    if abs((t - last_key).total_seconds()) > short_term_aggregation:
                        # Add new timestamp tuple to the medium term list
                        self.timestamps_medium_term.append(tuple((t, 1)))
                    else:
                        # Increase the count at the latest timestamp by 1
                        self.timestamps_medium_term[-1] = tuple(
                            (self.timestamps_medium_term[-1][0], self.timestamps_medium_term[-1][1] + 1))
                else:
                    # Add the first entry to the medium term list
                    self.timestamps_medium_term.append(tuple((t, 1)))

                # Remove the aggregated timestamp from the short term list
                self.timestamps_short_term.remove(t)

        # Start medium term aggregation
        for t in self.timestamps_medium_term:
            # Time difference between entry and current time in seconds
            sec = abs((ts - t[0]).total_seconds())
            # Check if medium term entry needs to be aggregated
            if sec > medium_term_aggregation:
                # Check if long term list is not empty
                if len(self.timestamps_long_term) > 0:
                    # Get the last timestamp from the long term list
                    last_key = self.timestamps_long_term[-1][0]
                    # Check if a new timestamp needs to be added to the long term list
                    if abs((t[0] - last_key).total_seconds()) > medium_term_aggregation:
                        # Add new timestamp tuple to the long term list
                        self.timestamps_long_term.append(tuple((t[0], t[1])))
                    else:
                        # Increase the count at the latest timestamp by 1
                        self.timestamps_long_term[-1] = tuple(
                            (self.timestamps_long_term[-1][0], self.timestamps_long_term[-1][1] + t[1]))
                else:
                    # Add the first entry to the long term list
                    self.timestamps_long_term.append(tuple((t[0], t[1])))
                # Remove the aggregated timestamp from the medium term list
                self.timestamps_medium_term.remove(t)

        # Start long term aggregation
        for t in self.timestamps_long_term:
            # Time difference between entry and current time in seconds
            sec = abs((ts - t[0]).total_seconds())
            # Check if long term entry needs to be removed
            if sec > long_term_aggregation:
                # Remove old timestamps from the long term list
                self.timestamps_long_term.remove(t)


    def update_reliability(self) -> None:
        for c in self.GET_nodes:
            c.update_reliability(len(self.timestamps_short_term), 0, 0, 1.0)
        for c in self.POST_nodes:
            c.update_reliability(len(self.timestamps_short_term), 0, 0, 1.0)
        for c in self.HEAD_nodes:
            c.update_reliability(len(self.timestamps_short_term), 0, 0, 1.0)
        for c in self.PUT_nodes:
            c.update_reliability(len(self.timestamps_short_term), 0, 0, 1.0)
        for c in self.DELETE_nodes:
            c.update_reliability(len(self.timestamps_short_term), 0, 0, 1.0)
        for c in self.OPTIONS_nodes:
            c.update_reliability(len(self.timestamps_short_term), 0, 0, 1.0)
        for c in self.PATCH_nodes:
            c.update_reliability(len(self.timestamps_short_term), 0, 0, 1.0)

    def __str__(self):
        return f"---- ROOT Node ----\n" \
               f"Core: {self.core_node}\n" \
               f"Initial Time: {self.init_time}\n" \
               f"# of Timestamps Short Term: {len(self.timestamps_short_term)}\n" \
               f"Timestamps Short Term: {self.timestamps_short_term}\n" \
               f"Timestamps Medium Term: {self.timestamps_medium_term}\n" \
               f"Timestamps Long Term: {self.timestamps_long_term}\n" \
               f"GET Nodes: {self.GET_nodes}\n" \
               f"POST Nodes: {self.POST_nodes}\n" \
               "---- End ROOT ----"


class DirNode(INode):
    """
    This class represents a directory node in the typing tree.

    Attributes
    ----------
    name: str
        Name of the directory
    children: list
        List of the children
    init_time: datetime
        The timestamp of the time when the node was created.
    timestamps_short_term: list
        The list of the shortterm timestamps.
    timestamps_medium_term: list
        The list of the medium term timestamps.
    timestamps_long_term: list
        The list of the long term timestamps.
    core_node: bool
        States if the node is a core node or not.
    reliability: float
        The reliability of the node.

    Methods
    ----------
    add_child(path_list, core)
        Adds a child node to the current node.
    add_timestamp(ts)
        Adds a timestamp to the list.
    aggregate(ts)
        Aggregates the tracked timestamps:
        - All timestamps older than 1h are aggregated in the window of the last 24h in 1h steps.
        - All timestamps older than 24h are aggregated in the window of the last 7d in 1d steps.
        - All timestamps older than 7d are deleted.
    update_reliability(parent_short_term_length, parent_medium_term_length, parent_long_term_length, calculated_reliability)
        Calculates the node reliability with the information gathered from the parent.
    """

    def __init__(self, dir_name: str) -> None:
        """
        Parameters
        ----------
        dir_name: str
            Name of the directory.
        """

        self.name = dir_name

        self.children = []

        self.init_time = None

        self.timestamps_short_term = []
        self.timestamps_medium_term = []
        self.timestamps_long_term = []

        self.core_node = False

        self.reliability = 0.0


    def add_child(self, path_list: List, core: bool) -> INode:
        """
        Adds a child node to the current node.

        Parameters
        ----------
        path_list: list
            The list of the remaining path tokens of the request path.
        core: bool
            If the node is a core node or not.

        Returns
        ----------
        INode
            The reference of the Resource Node of this specific path.
        """

        if len(path_list) == 1:  # Resource
            res_name = path_list[0]
            child = next((x for x in self.children if (isinstance(x, ResourceNode) and x.name == res_name)), None)
            if child is None:  # Resource doesn't exist yet
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
        else:  # Directory
            dir_name = path_list[0]
            child = next((x for x in self.children if (isinstance(x, DirNode) and x.name == dir_name)), None)
            if child is None:  # Directory doesn't exist yet
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
        """
        Adds a timestamp to the list.

        Parameters
        ----------
        ts: datetime
            The timestamp to be added.
        """

        self.timestamps_short_term.append(ts)
        self.aggregate(ts)


    def aggregate(self, ts: datetime) -> None:
        """
        Aggregates the tracked timestamps:
        - All timestamps older than 1h are aggregated in the window of the last 24h in 1h steps.
        - All timestamps older than 24h are aggregated in the window of the last 7d in 1d steps.
        - All timestamps older than 7d are deleted.

        Parameters
        ----------
        ts: datetime
            The timestamp that just was added and is used as a reference.
        """

        # Set the short term aggregation time in seconds (Should be 3600)
        short_term_aggregation = 5.0
        # Set the medium term aggregation time in seconds (Should be 86400)
        medium_term_aggregation = 20.0
        # Set the long term aggregation time in seconds (Should be 604800)
        long_term_aggregation = 100.0

        # Start short term aggregation
        for t in self.timestamps_short_term:
            # Time difference between entry and current time in seconds
            sec = abs((ts - t).total_seconds())
            # Check if short term entry needs to be aggregated
            if sec > short_term_aggregation:
                # Check if medium term list is not empty
                if len(self.timestamps_medium_term) > 0:
                    # Get the last timestamp from the medium term list
                    last_key = self.timestamps_medium_term[-1][0]
                    # Check if a new timestamp needs to be added to the medium term list
                    if abs((t - last_key).total_seconds()) > short_term_aggregation:
                        # Add new timestamp tuple to the medium term list
                        self.timestamps_medium_term.append(tuple((t, 1)))
                    else:
                        # Increase the count at the latest timestamp by 1
                        self.timestamps_medium_term[-1] = tuple(
                            (self.timestamps_medium_term[-1][0], self.timestamps_medium_term[-1][1] + 1))
                else:
                    # Add the first entry to the medium term list
                    self.timestamps_medium_term.append(tuple((t, 1)))
                # Remove the aggregated timestamp from the short term list
                self.timestamps_short_term.remove(t)

        # Start medium term aggregation
        for t in self.timestamps_medium_term:
            # Time difference between entry and current time in seconds
            sec = abs((ts - t[0]).total_seconds())
            # Check if medium term entry needs to be aggregated
            if sec > medium_term_aggregation:
                # Check if long term list is not empty
                if len(self.timestamps_long_term) > 0:
                    # Get the last timestamp from the long term list
                    last_key = self.timestamps_long_term[-1][0]
                    # Check if a new timestamp needs to be added to the long term list
                    if abs((t[0] - last_key).total_seconds()) > medium_term_aggregation:
                        # Add new timestamp tuple to the long term list
                        self.timestamps_long_term.append(tuple((t[0], t[1])))
                    else:
                        # Increase the count at the latest timestamp by 1
                        self.timestamps_long_term[-1] = tuple(
                            (self.timestamps_long_term[-1][0], self.timestamps_long_term[-1][1] + t[1]))
                else:
                    # Add the first entry to the long term list
                    self.timestamps_long_term.append(tuple((t[0], t[1])))
                # Remove the aggregated timestamp from the medium term list
                self.timestamps_medium_term.remove(t)

        # Start long term aggregation
        for t in self.timestamps_long_term:
            # Time difference between entry and current time in seconds
            sec = abs((ts - t[0]).total_seconds())
            # Check if long term entry needs to be removed
            if sec > long_term_aggregation:
                # Remove old timestamps from the long term list
                self.timestamps_long_term.remove(t)


    def update_reliability(self, parent_short_term_length: int, parent_medium_term_length: int,
                           parent_long_term_length: int, calculated_reliability: float) -> None:
        """
        Calculates the node reliability with the information gathered from the parent.

        Parameters
        ----------
        parent_short_term_length: int
            Amount of short term timestamps in parent
        parent_medium_term_length: int
            Amount of medium term timestamps in parent
        parent_long_term_length: int
            Amount of long term timestamps in parent
        calculated_reliability: float
            Current path reliability to this point
        """

        medium_term_length = 0
        long_term_length = 0
        for t in self.timestamps_medium_term:
            medium_term_length = medium_term_length + t[1]

        for t in self.timestamps_long_term:
            long_term_length = long_term_length + t[1]

        # If no core node the reliability is calculated by number of time stamps of this node divided by the number of time stamps of the parent node
        if not self.core_node:
            # self.reliability = len(self.timestamps_short_term) / parent_length
            ts = datetime.now()
            # Check if node is up less than 1h
            if (ts - self.init_time).total_seconds() < 3600:
                self.reliability = len(self.timestamps_short_term) / parent_short_term_length

            # Check if node is up more than 1h and less than 24h
            elif 3600 < (ts - self.init_time).total_seconds() < 86400:
                self.reliability = (len(self.timestamps_short_term) + medium_term_length) / (
                            parent_short_term_length + parent_medium_term_length)
            # Default Node is up more than 24h
            else:
                self.reliability = (len(self.timestamps_short_term) + medium_term_length + long_term_length) / (
                            parent_short_term_length + parent_medium_term_length + parent_long_term_length)

        for c in self.children:
            c.update_reliability(len(self.timestamps_short_term), medium_term_length, long_term_length,
                                 calculated_reliability * self.reliability)


    def __str__(self):
        return f"---- DIR Node: {self.name} ----\n" \
               f"Core: {self.core_node}\n" \
               f"Initial Time: {self.init_time}\n" \
               f"# of Timestamps Short Term: {len(self.timestamps_short_term)}\n" \
               f"Timestamps Short Term: {self.timestamps_short_term}\n" \
               f"Timestamps Medium Term: {self.timestamps_medium_term}\n" \
               f"Timestamps Long Term: {self.timestamps_long_term}\n" \
               f"Reliability: {self.reliability}\n" \
               f"Children: {self.children}\n" \
               f"---- End Dir: {self.name} ----"


    def __repr__(self):
        return textwrap.indent(f"\n{self.__str__()}\n", 4 * ' ')


class ResourceNode(INode):
    """
    This class represents a resource node in the typing tree.

    Attributes
    ----------
    name: str
        Name of the resource
    init_time: datetime
        The timestamp of the time when the node was created.
    timestamps_short_term: list
        The list of the shortterm timestamps.
    timestamps_medium_term: list
        The list of the medium term timestamps.
    timestamps_long_term: list
        The list of the long term timestamps.
    core_node: bool
        States if the node is a core node or not.
    reliability: float
        The reliability of the node.
    path_reliability: float
        The reliability of the path.

    Methods
    ----------
    add_timestamp(ts)
        Adds a timestamp to the list.
    aggregate(ts)
        Aggregates the tracked timestamps:
        - All timestamps older than 1h are aggregated in the window of the last 24h in 1h steps.
        - All timestamps older than 24h are aggregated in the window of the last 7d in 1d steps.
        - All timestamps older than 7d are deleted.
    update_reliability(parent_short_term_length, parent_medium_term_length, parent_long_term_length, calculated_reliability)
        Calculates the node reliability with the information gathered from the parent.
    """

    def __init__(self, resource_name: str) -> None:
        """
        Parameters
        ----------
        resource_name: str
            Name of the resource.
        """

        self.name = resource_name

        self.init_time = None

        self.timestamps_short_term = []
        self.timestamps_medium_term = []
        self.timestamps_long_term = []

        self.core_node = False

        self.reliability = 0.0
        self.path_reliability = 0.0


    def add_timestamp(self, ts: datetime) -> None:
        """
        Adds a timestamp to the list.

        Parameters
        ----------
        ts: datetime
            The timestamp to be added.
        """

        self.timestamps_short_term.append(ts)
        self.aggregate(ts)


    def aggregate(self, ts: datetime) -> None:
        """
        Aggregates the tracked timestamps:
        - All timestamps older than 1h are aggregated in the window of the last 24h in 1h steps.
        - All timestamps older than 24h are aggregated in the window of the last 7d in 1d steps.
        - All timestamps older than 7d are deleted.

        Parameters
        ----------
        ts: datetime
            The timestamp that just was added and is used as a reference.
        """

        # Set the short term aggregation time in seconds (Should be 3600)
        short_term_aggregation = 5.0
        # Set the medium term aggregation time in seconds (Should be 86400)
        medium_term_aggregation = 20.0
        # Set the long term aggregation time in seconds (Should be 604800)
        long_term_aggregation = 100.0

        # Start short term aggregation
        for t in self.timestamps_short_term:
            # Time difference between entry and current time in seconds
            sec = abs((ts - t).total_seconds())
            # Check if short term entry needs to be aggregated
            if sec > short_term_aggregation:
                # Check if medium term list is not empty
                if len(self.timestamps_medium_term) > 0:
                    # Get the last timestamp from the medium term list
                    last_key = self.timestamps_medium_term[-1][0]
                    # Check if a new timestamp needs to be added to the medium term list
                    if abs((t - last_key).total_seconds()) > short_term_aggregation:
                        # Add new timestamp tuple to the medium term list
                        self.timestamps_medium_term.append(tuple((t, 1)))
                    else:
                        # Increase the count at the latest timestamp by 1
                        self.timestamps_medium_term[-1] = tuple(
                            (self.timestamps_medium_term[-1][0], self.timestamps_medium_term[-1][1] + 1))
                else:
                    # Add the first entry to the medium term list
                    self.timestamps_medium_term.append(tuple((t, 1)))
                # Remove the aggregated timestamp from the short term list
                self.timestamps_short_term.remove(t)

        # Start medium term aggregation
        for t in self.timestamps_medium_term:
            # Time difference between entry and current time in seconds
            sec = abs((ts - t[0]).total_seconds())
            # Check if medium term entry needs to be aggregated
            if sec > medium_term_aggregation:
                # Check if long term list is not empty
                if len(self.timestamps_long_term) > 0:
                    # Get the last timestamp from the long term list
                    last_key = self.timestamps_long_term[-1][0]
                    # Check if a new timestamp needs to be added to the long term list
                    if abs((t[0] - last_key).total_seconds()) > medium_term_aggregation:
                        # Add new timestamp tuple to the long term list
                        self.timestamps_long_term.append(tuple((t[0], t[1])))
                    else:
                        # Increase the count at the latest timestamp by 1
                        self.timestamps_long_term[-1] = tuple(
                            (self.timestamps_long_term[-1][0], self.timestamps_long_term[-1][1] + t[1]))
                else:
                    # Add the first entry to the long term list
                    self.timestamps_long_term.append(tuple((t[0], t[1])))
                # Remove the aggregated timestamp from the medium term list
                self.timestamps_medium_term.remove(t)

        # Start long term aggregation
        for t in self.timestamps_long_term:
            # Time difference between entry and current time in seconds
            sec = abs((ts - t[0]).total_seconds())
            # Check if long term entry needs to be removed
            if sec > long_term_aggregation:
                # Remove old timestamps from the long term list
                self.timestamps_long_term.remove(t)


    def update_reliability(self, parent_short_term_length: int, parent_medium_term_length: int,
                           parent_long_term_length: int, calculated_reliability: float) -> None:
        """
        Calculates the node reliability with the information gathered from the parent.

        Parameters
        ----------
        parent_short_term_length: int
            Amount of short term timestamps in parent
        parent_medium_term_length: int
            Amount of medium term timestamps in parent
        parent_long_term_length: int
            Amount of long term timestamps in parent
        calculated_reliability: float
            Current path reliability to this point
        """
        
        if not self.core_node:
            medium_term_length = 0
            long_term_length = 0
            for t in self.timestamps_medium_term:
                medium_term_length = medium_term_length + t[1]

            for t in self.timestamps_long_term:
                long_term_length = long_term_length + t[1]

            # If no core node the reliability is calculated by number of time stamps of this node divided by the number of time stamps of the parent node
            if not self.core_node:
                # self.reliability = len(self.timestamps_short_term) / parent_length
                ts = datetime.now()
                # Check if node is up less than 1h
                if (ts - self.init_time).total_seconds() < 3600:
                    self.reliability = len(self.timestamps_short_term) / parent_short_term_length

                # Check if node is up more than 1h and less than 24h
                elif 3600 < (ts - self.init_time).total_seconds() < 86400:
                    self.reliability = (len(self.timestamps_short_term) + medium_term_length) / (
                            parent_short_term_length + parent_medium_term_length)
                # Default Node is up more than 24h
                else:
                    self.reliability = (len(self.timestamps_short_term) + medium_term_length + long_term_length) / (
                            parent_short_term_length + parent_medium_term_length + parent_long_term_length)

            self.path_reliability = calculated_reliability * self.reliability


    def __str__(self):
        return f"---- RES Node: {self.name} ----\n" \
               f"Core: {self.core_node}\n" \
               f"Initial Time: {self.init_time}\n" \
               f"# of Timestamps Short Term: {len(self.timestamps_short_term)}\n" \
               f"Timestamps Short Term: {self.timestamps_short_term}\n" \
               f"Timestamps Medium Term: {self.timestamps_medium_term}\n" \
               f"Timestamps Long Term: {self.timestamps_long_term}\n" \
               f"Reliability: {self.reliability}\n" \
               f"Path Reliability: {self.path_reliability}\n" \
               f"---- End RES: {self.name} ----"


    def __repr__(self):
        return textwrap.indent(f"\n{self.__str__()}\n", 4 * ' ')
