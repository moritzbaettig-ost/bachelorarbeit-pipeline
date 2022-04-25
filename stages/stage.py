from abc import ABC, abstractmethod
from dtos import DTO
import stages
# from stages import Stage


class Stage(ABC):
    def __init__(self, successor):
        self.successor = successor

    @abstractmethod
    def run(self, dto: DTO):
        pass
