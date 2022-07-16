from dataclasses import dataclass
from message import IDSHTTPMessage
from type import Type


@dataclass
class DTO:
    pass


@dataclass
class AcquisitionFilterDTO(DTO):
    message: IDSHTTPMessage


@dataclass
class FilterTypingDTO(DTO):
    message: IDSHTTPMessage


@dataclass
class TypingExtractionDTO(DTO):
    message: IDSHTTPMessage
    type: Type

@dataclass
class ExtractionModelDTO(DTO):
    features: dict
    type: Type
    