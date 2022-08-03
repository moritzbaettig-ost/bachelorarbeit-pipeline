import urllib.parse as parser
from message import IDSHTTPMessage
from stages.filter import FilterPluginInterface


class Plugin(FilterPluginInterface):
    """
    This plugin filters all requests that use double encoded strings.

    Methods
    ----------
    filter_request(message)
        Returns if the given message should be filtered or not.
    """

    def filter_request(self, message: IDSHTTPMessage) -> tuple[bool, str, str]:
        """
        Returns if the given message should be filtered or not.

        Parameters
        ----------
        message: IDSHTTPMessage
            The HTTP message that should be filtered or not.

        Returns
        ----------
        tuple[bool, str]
            If the message should be filtered and the reason for it.
        """
        
        if message.query != '':
            query1 = message.query
            query2 = parser.unquote(query1)
            if(query1!=query2):
                return (True, "Double Encoded Path Query detected", "Double Encoding Filter Plugin")
        if message.body != '':
            body1 = message.body
            body2 = parser.unquote(body1)
            if(body1 != body2):
                return (True, "Double Encoded Body detected", "Double Encoding Filter Plugin")
        return (False, "", "Double Encoding Filter Plugin")
