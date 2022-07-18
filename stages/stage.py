from abc import ABC, abstractmethod
from dtos import DTO



class Stage(ABC):
    """
    An interface that defines the run-method for all pipeline stages.

    Methods
    ----------
    run(dto)
        Triggers the functionality of the pipeline stage.
    """

    @abstractmethod
    def run(self, dto: DTO) -> None:
        """
        Triggers the functionality of the pipeline stage.

        Parameters
        ----------
        dto : DTO
            The data transer object that is received from the previous stage.
        """
        
        pass
