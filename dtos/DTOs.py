from dataclasses import dataclass


@dataclass
class DTO:
    pass


@dataclass
class AcquisitionFilterDTO(DTO):
    request: str