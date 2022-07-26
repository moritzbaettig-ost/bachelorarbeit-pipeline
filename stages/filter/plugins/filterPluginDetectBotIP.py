from collections import namedtuple
import time
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

        # Checks if the source address is in the blocklist
        if message.source_address in self.blocklist.get_ip_blocklist():
            return (True, "Blocked ")
        return (False, "")


class IPBlocklist:
    """
    Class which implements the singelton pattern for the IPBlocklist Update Job.
    This class updates the Blocklist every 10 min from https://feodotracker.abuse.ch/downloads/ipblocklist_aggressive.csv.

    Attributes
    ----------
    ip_blocklist: list
    daemon: Thread

    Methods
    ----------
    parse_validate_csv(response, columns)
        This method parses the csv data and checks the downloaded data
    get_ip_aggressive(interval_sec)
        Downloads the new Blocklist definitions.
    get_ip_blocklist()
        Returns the IPBlocklist
    """

    # Class constructor which initiates the Update Job
    def __init__(self):
        self.ip_blocklist = []
        self.ip = namedtuple('IPAddress', ['first_seen', 'ipaddress', 'port', 'last_seen', 'family'])
        # Run Update Job every 10 min
        self.daemon = Thread(target=self.get_ip_aggressive, args=(600,), daemon=True, name='UpdateIPBlocklistBackground')
        self.daemon.start()

    # Singelton Pattern which creates an instance or returns the reference to an existing instance
    def __new__(cls, *args, **kw):
        if not hasattr(cls, '_instance'):
            orig = super(IPBlocklist, cls)
            cls._instance = orig.__new__(cls)
        return cls._instance

    def parse_validate_csv(self, response: requests, columns: int):
        """
        Parse the downloaded csv file and validates the data

        Parameters
        ----------
        response: requests
            This parameter is the downloaded csv file.
        columns: int
            Number of columns from the csv file

        Returns
        ----------
        rows: list
            List of rows from the csv file
        """
        # split lines and convert into ascii
        rows = [line.decode('ascii', errors='ignore') for line in response.content.splitlines()]
        # remove commented lines & split
        rows = [row.split(',') for row in rows if not row.startswith('#')]
        # validate column count & return
        rows = [row for row in rows if len(row) == columns]
        return rows

    def get_ip_aggressive(self, interval_sec: int) -> None:
        """
        This function downloads the newest Blocklist in a specific interval

        Parameters
        ----------
        interval_sec: int
            Wait for this number of seconds

        """
        #run forever
        while True:
            # Path of the newest Blocklist
            url = "https://feodotracker.abuse.ch/downloads/ipblocklist_aggressive.csv"
            # Download the Blocklist
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
            # Set the newest Blocklist
            self.ip_blocklist = [i[1] for i in data]
            time.sleep(interval_sec)

    def get_ip_blocklist(self):
        """
        Returns the blocklist.

        Returns
        ----------
        ip_blocklist: list
        """
        return self.ip_blocklist
