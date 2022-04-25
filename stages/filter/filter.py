import importlib
import sys
from dtos.DTOs import AcquisitionFilterDTO
from stages import Stage


class FilterPluginInterface:
    def filter_request(self, req: str) -> tuple[bool, str]:
        pass


class RequestFilter(Stage):
    # TODO: Insert type of successor
    # TODO: Remove filter_plugin param and import all filter plugins in directory automatically. Use multiple filters.
    def __init__(self, successor: None, filter_plugin: str):
        sys.path.append('./stages/filter')
        if filter_plugin is not None:
            self.plugin = importlib.import_module('filterPlugin'+filter_plugin, ".").Plugin()
        else:
            self.plugin = importlib.import_module('filterPluginDefault', ".").Plugin()

        super().__init__(successor)

    def run(self, dto: AcquisitionFilterDTO):
        t = self.plugin.filter_request(dto.request)
        if not t[0]:
            # TODO: Pass req string to successor
            print(self.plugin.filter_request(dto.request))
        else:
            print("Filter Alert: "+t[1])
            # TODO: Throw Filter Alert
