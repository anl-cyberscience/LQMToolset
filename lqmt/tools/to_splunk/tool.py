import logging
import requests
import time
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from lqmt.lqm.data import AlertAction
from lqmt.lqm.tool import Tool
from lqmt.tools.to_splunk.splunk_api import ApiCaller



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

        self.apicaller = ApiCaller(
                self._config.host,
                self._config.port,
                self._config.username,
                self._config.password,
                cert_check=self._config.cert_check,
                source=self._config.source,
                sourcetype=self._config.sourcetype
        )

    def initialize(self):
        super().initialize()

    def process(self, alert):
        """
        Process function. Handles the processing of data for the tool. 
        """
        self.apicaller.send_message(self.create_message(alert))

    @staticmethod
    def create_message(alert):
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
        self.apicaller.__exit__()
        pass
