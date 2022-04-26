import importlib
import sys
import os
from dtos.DTOs import AcquisitionFilterDTO
from stages import Stage


class FilterPluginInterface:
    def filter_request(self, req: str) -> tuple[bool, str]:
        pass


class RequestFilter(Stage):
    # TODO: Insert type of successor
    def __init__(self, successor: None):
        if len(os.listdir('./stages/filter/plugins')) == 0:
            sys.exit("No filter plugin detcted. Please place default filter plugin in the filter plugis directory.")
        sys.path.append('./stages/filter/plugins')
        self.plugins = [
            importlib.import_module(f.split('.')[0], '.').Plugin()
            for f in next(os.walk('stages/filter/plugins'))[2]
        ]
        super().__init__(successor)

    def run(self, dto: AcquisitionFilterDTO):
        for plugin in self.plugins:
            filter_response = plugin.filter_request(dto.message)
            if filter_response[0]:
                # TODO: Throw Filter Alert
                print("Filter Alert: "+filter_response[1])
                return
        # TODO: Pass req string to successor
        print(dto.message)
