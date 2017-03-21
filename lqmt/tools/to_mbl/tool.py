import logging
from lqmt.lqm.tool import Tool
from lqmt.lqm.data import AlertAction
from lqmt.tools.to_splunk.splunk_api import create_message, ApiHandler
from lqmt.lqm.parsers.FlexTransform.parser import FlexTransformParser


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


class ToMBL(Tool):
    def __init__(self, config):
        """
        ToMBL tool. Used to push data to MBL using the Splunk Web API.
        :param config: configuration file
        """
        super().__init__(config, [AlertAction.get('All')])
        self._logger = logging.getLogger("LQMT.ToolName.{0}".format(self.getName()))
        self.alerts = {}

        self._parser = FlexTransformParser({'mbl': 'resources/sampleConfigurations/MBL.cfg'})
        for file_type, source_config in self._config.source_configs.items():
            self._parser.add_parser(file_type, source_config)

        # commenting out splunk handler until data is formmated correctly first
        # self.handler = ApiHandler(
        #     self._config.host,
        #     self._config.port,
        #     self._config.username,
        #     self._config.password,
        #     cert_check=self._config.cert_check,
        #     source=self._config.source,
        # )

    def initialize(self):
        super().initialize()

    def process(self, alert, meta):
        """
        Process function. Handles the processing of data for the tool. 
        """
        # parse alert using custom parser
        mbl_alert = self._parser.custom_parser(alert, meta['PayloadFormat'], 'mbl')

        # pop alert data from list
        mbl_alert = mbl_alert.pop()

        # put alert data into a dictionary. key is generated from a hash of the list
        self.alerts[hash(str(mbl_alert))] = mbl_alert

    def commit(self):
        print("committing")
        print(self.sort_alert_dictionary())

        # eventually, this is where the message will be sent from
        # self.handler.send_message(create_message(alert), sourcetype="PULL FROM ALERT")

    def cleanup(self):
        pass

    def parse_alert_dictionary(self):
        """
        :return: returns a list of splunk/mbl formatted string generated from the alert dictionary
        """
        messages = []
        for dict_key, alert_data in self.alerts.items():
            alert_list = []
            for alert_dictionary in alert_data:
                for key, data in alert_dictionary.items():
                    alert_list.append(str(key)+": "+str(data))
            messages.append(' '.join(alert_list))

        return messages
