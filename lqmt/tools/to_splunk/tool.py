import logging
import requests
from lqmt.lqm.tool import Tool
from lqmt.lqm.data import AlertAction
from lqmt.tools.to_splunk.splunk_api import ApiCaller, create_message
from requests.packages.urllib3.exceptions import InsecureRequestWarning


class ToSplunk(Tool):
    def __init__(self, config):
        """
        ToFlexText tool. Used to reformat CTI data in a user configured manner.

        :param config: configuration file
        """
        super().__init__(config, [AlertAction.get('All')])
        self._logger = logging.getLogger("LQMT.FlexText.{0}".format(self.getName()))
        self._splunk_token = ""

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
        self.apicaller.send_message(create_message(alert))

    def commit(self):
        pass

    def cleanup(self):
        self.apicaller.__exit__()
        pass
