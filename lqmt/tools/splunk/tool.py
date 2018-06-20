import logging
import requests
from lqmt.lqm.tool import Tool
from lqmt.lqm.data import AlertAction
from lqmt.lqm.data import QueryFile
from lqmt.tools.splunk.splunk_api import ApiHandler, create_message
from requests.packages.urllib3.exceptions import InsecureRequestWarning


class ToSplunk(Tool):
    def __init__(self, config):
        """
        ToSplunk tool. Used to push data to Splunk using Splunk web API.

        :param config: configuration file
        """
        super().__init__(config, [AlertAction.get('All')])
        self._logger = logging.getLogger("LQMT.ToSplunk.{0}".format(self.getName()))
        self._splunk_token = ""

        if self._config.cert_check is False:
            requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

        self.handler = ApiHandler(
            self._config.host,
            self._config.port,
            self._config.username,
            self._config.password,
            cert_check=self._config.cert_check,
            source=self._config.source,
            sourcetype=self._config.sourcetype,
            index=self._config.index
        )

    def initialize(self):
        super().initialize()

    def process(self, alert):
        """
        Process function. Handles the processing of data for the tool. 
        """
        self.handler.stream_data(create_message(alert))

    def commit(self):
        pass

    def cleanup(self):
        self.handler.__exit__()

class SplunkRSA(Tool):
    def __init__(self, config):
        """
        ToSplunk tool. Used to push data to Splunk using Splunk web API.

        :param config: configuration file
        """
        super().__init__(config, [AlertAction.get('Query')])
        self._logger = logging.getLogger("LQMT.SplunkRSA.{0}".format(self.getName()))
        self._splunk_token = ""

        if self._config.cert_check is False:
            requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

        self.handler = ApiHandler(
            self._config.host,
            self._config.port,
            self._config.username,
            self._config.password,
            cert_check=self._config.cert_check,
            source=self._config.source,
            sourcetype=self._config.sourcetype,
            index=self._config.index
        )

    def initialize(self):
        super().initialize()

    def process(self, query):
        """
        Process function. Handles the processing of data for the tool. 
        """
        temp = query.getAllFields(dictionary=True)
        print(temp)
        search = f""
        print(search)
        response = self.handler.submit_search(search)
        if response.text:
            print("Results found!")
        else:
            print("No results found!")
        print(response)
        

    def commit(self):
        pass

    def cleanup(self):
        self.handler.__exit__()
