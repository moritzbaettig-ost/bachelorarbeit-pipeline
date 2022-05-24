import urllib.parse as parser
from message import IDSHTTPMessage
from stages.filter import FilterPluginInterface


class Plugin(FilterPluginInterface):
    def filter_request(self, message: IDSHTTPMessage) -> tuple[bool, str]:
        if message.query != '':
            query1 = message.query
            query2 = parser.unquote(query1)
            if(query1!=query2):
                return (True, "Double Encoded Path Query detected")
        return (False, "")
