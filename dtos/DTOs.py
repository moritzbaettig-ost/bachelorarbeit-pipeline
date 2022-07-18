from dataclasses import dataclass
from message import IDSHTTPMessage
from type import Type


@dataclass
class DTO:
    """
    An interface used to represent data that is transferred between two pipeline stages.
    """

    pass


@dataclass
class AcquisitionFilterDTO(DTO):
    """
    The data transfer object to transport data between the acquisition and the filter stage.

    Attributes
    ----------
    message : IDSHTTPMessage
        The HTTP request that has been acquired and has to be analyzed.
    """

    message: IDSHTTPMessage


@dataclass
class FilterTypingDTO(DTO):
    """
    The data transfer object to transport data between the filter and the typing stage.

    Attributes
    ----------
    message : IDSHTTPMessage
        The HTTP request that has been acquired and has to be analyzed.
    """

    message: IDSHTTPMessage


@dataclass
class TypingExtractionDTO(DTO):
    """
    The data transfer object to transport data between the typing and the extraction stage.

    Attributes
    ----------
    message : IDSHTTPMessage
        The HTTP request that has been acquired and has to be analyzed.
    type : Type
        The type of the HTTP request that has to be analyzed.
    """

    message: IDSHTTPMessage
    type: Type
    

@dataclass
class ExtractionModelDTO(DTO):
    """
    The data transfer object to transport data between the extraction and the model stage.

    Attributes
    ----------
    features : dict
        The dictionary containing the extracted features for the Machine Learning model.
    type : Type
        The type of the HTTP request that has to be analyzed.
    """

    features: dict
    type: Type
    