from abc import ABC, abstractmethod
from dtos import DTO



class Stage(ABC):
    def __init__(self, successor: 'Stage'):
        self.successor = successor

    @abstractmethod
    def run(self, dto: DTO):
        pass
