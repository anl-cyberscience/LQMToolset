import logging
from lqmt.lqm.tool import Tool
from lqmt.lqm.data import AlertAction
from lqmt.tools.to_splunk.splunk_api import create_message, ApiHandler


def field_remapping(alert):
    """
    Function used to translate field mappings from the intermediate data format to the the mbl supported format
    :param alert:
    :return:
    """
    mbl_lexicon = {
        'blocking': {},
        'spearphish': {},
        'malware': {}
    }
    pass


class ToMBL(Tool):
    def __init__(self, config):
        """
        ToMBL tool. Used to push data to MBL using the Splunk Web API.
        :param config: configuration file
        """
        super().__init__(config, [AlertAction.get('All')])
        self._logger = logging.getLogger("LQMT.ToolName.{0}".format(self.getName()))

        self.handler = ApiHandler(
            self._config.host,
            self._config.port,
            self._config.username,
            self._config.password,
            cert_check=self._config.cert_check,
            source=self._config.source,
        )

    def initialize(self):
        super().initialize()

    def process(self, alert):
        """
        Process function. Handles the processing of data for the tool. 
        """
        self.handler.send_message(create_message(alert), sourcetype="PULL FROM ALERT")

    def commit(self):
        pass

    def cleanup(self):
        pass
