import logging
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import time
from xml.etree import ElementTree
from lqmt.lqm.data import AlertAction
from lqmt.lqm.tool import Tool


class ToSplunk(Tool):
    def __init__(self, config):
        """
        ToFlexText tool. Used to reformat CTI data in a user configured manner.

        :param config: configuration file
        """
        super().__init__(config, [AlertAction.get('All')])
        self._logger = logging.getLogger("LQMT.FlexText.{0}".format(self.getName()))
        self._splunk_token = ""

        # self.api = ApiCaller(self._config.host, self._config.port, self._config.username, self._config.password)
        # self.api.authenticate()
        if self._config.cert_check is False:
            requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

        with ApiCaller(
                self._config.host,
                self._config.port,
                self._config.username,
                self._config.password,
                cert_check=self._config.cert_check
        ) as api:
            self._splunk_token = api.splunk_token['Authorization']
            print(api.splunk_token)

    def initialize(self):
        super().initialize()

    def process(self, alert):
        """
        Process function. Handles the processing of data for the tool. 
        """
        print(self.createmessage(alert))
        with ApiCaller(
                self._config.host,
                self._config.port,
                splunk_token=self._splunk_token,
                cert_check=self._config.cert_check
        ) as api:
            api.authenticate()

        pass

    def submit_job(self):
        response = requests.post(
            self._config.host,
            auth=(self._config.username, self._config.username),
            verify=self._config.cert_check,
            data=None
        )

        if response.ok:
            pass
        else:
            print("Error authenticating request.")
            return None

    @staticmethod
    def createmessage(alert):
        """
        Creates a formatted message for Splunk that contains parsed data from FlexT. Currently returns all non-empty
        parsed data.

        :param alert: Parsed alert data from FlexT
        :return: Returns formatted string.
        """
        data = alert.getAllFields(dictionary=True, parseEmpty=True)
        message = "{0} LQMT: ".format(time.asctime())
        for key, value in data.items():
            message += "{0}={1} ".format(key, value)

        return message

    def commit(self):
        pass

    def cleanup(self):
        pass


class ApiCaller:
    """
    Class for handling API calls to Splunks REST Api. This class might end up being redundant depending on a few things,
    but that will be fleshed out further as the tool is built.
    """

    def __init__(self, host=None, port=None, username=None, password=None, splunk_token="", cert_check=True):
        self.host = host
        self.port = port
        self.cert_check = cert_check
        self.url = self.host + ":" + str(self.port)
        self.username = username
        self.password = password
        self.response = ""
        self.requests = requests
        self.job_status = ""
        self.job_id = ""
        self.splunk_token = {'Authorization': splunk_token}

    def __enter__(self):
        self.authenticate()
        return self

    def __exit__(self, exc_t, exc_v, trace):
        self.requests.post(url=self.url, headers={'Connection': 'close'}, verify=self.cert_check)

    def authenticate(self):
        """
        Method for authenticating against Splunk's REST Api. Returns a session token that will be used for future
        connections
        :return: Session token
        """
        if not self.splunk_token['Authorization']:
            print("Authenticating")
            data = {
                'username': self.username,
                'password': self.password
            }
            r = self.requests.post(
                self.url + "/services/auth/login/",
                data=data,
                verify=self.cert_check
            )
            print(r.status_code)
            data = ElementTree.fromstring(r.content)
            self.splunk_token['Authorization'] = "Splunk " + data[0].text

            return self.splunk_token
