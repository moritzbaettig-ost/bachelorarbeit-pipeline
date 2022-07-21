from message import IDSHTTPMessage
from stages.filter import FilterPluginInterface


class Plugin(FilterPluginInterface):
    """
    This plugin represents the default function of the filter stage.

    Methods
    ----------
    filter_request(message)
        Returns if the given message should be filtered or not.
    """

    def filter_request(self, message: IDSHTTPMessage) -> tuple[bool, str]:
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
        
        return (False, "")
