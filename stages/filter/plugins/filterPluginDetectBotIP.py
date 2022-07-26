import time
from collections import namedtuple
from threading import Thread
import requests
from message import IDSHTTPMessage
from stages.filter import FilterPluginInterface


class Plugin(FilterPluginInterface):
    """
    This plugin filters all requests which are listed as a Bot on feodotracker.abuse.ch.

    Methods
    ----------
    filter_request(message)
        Returns if the given message should be filtered or not.
    """

    def __init__(self):
        self.blocklist = IPBlocklist()

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

        if message.source_address in self.blocklist.get_ip_blocklist():
            return (True, "Blocked ")
        return (False, "")


class IPBlocklist:
    def __init__(self):
        self.ip_blocklist = []
        self.daemon = Thread(target=self.get_ip_aggressive, args=(3,), daemon=True, name='Background')
        self.daemon.start()

    def __new__(cls, *args, **kw):
        if not hasattr(cls, '_instance'):
            orig = super(IPBlocklist, cls)
            cls._instance = orig.__new__(cls)
        return cls._instance


    ip = namedtuple('IPAddress', ['first_seen', 'ipaddress', 'port', 'last_seen', 'family'])

    def parse_validate_csv(self, response, columns):
        # split lines and convert into ascii
        rows = [line.decode('ascii', errors='ignore') for line in response.content.splitlines()]
        # remove commented lines & split
        rows = [row.split(',') for row in rows if not row.startswith('#')]
        # validate column count & return
        rows = [row for row in rows if len(row) == columns]
        return rows

    def get_ip_aggressive(self, interval_sec: int) -> None:
        #run forever
        while True:
            url = "https://feodotracker.abuse.ch/downloads/ipblocklist_aggressive.csv"
            response = requests.get(url)
            if not response.status_code == 200:
                raise Exception('Unable to fetch AbuseCh list: {url}')
            iplist = self.parse_validate_csv(response=response, columns=6)
            data = []
            for row in iplist:
                data.append(self.ip(
                    first_seen=row[0],
                    ipaddress=row[1],
                    port=row[2],
                    last_seen=row[3],
                    family=row[5]
                ))
            self.ip_blocklist = [i[1] for i in data]
            time.sleep(interval_sec)

    def get_ip_blocklist(self):
        return self.ip_blocklist
