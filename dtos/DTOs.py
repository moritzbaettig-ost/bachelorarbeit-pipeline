from dataclasses import dataclass
from message import IDSHTTPMessage


@dataclass
class DTO:
    pass


@dataclass
class AcquisitionFilterDTO(DTO):
    message: IDSHTTPMessage