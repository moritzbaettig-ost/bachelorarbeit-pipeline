from message import IDSHTTPMessage
from stages.filter import FilterPluginInterface


class Plugin(FilterPluginInterface):
    def filter_request(self, message: IDSHTTPMessage) -> tuple[bool, str]:
        return (False, "")
