import logging
from lqmt.lqm.tool import Tool
from lqmt.lqm.data import AlertAction
from lqmt.tools.to_splunk.splunk_api import ApiHandler
from lqmt.lqm.parsers.FlexTransform.parser import FlexTransformParser
import hashlib


class ToMBL(Tool):
    def __init__(self, config):
        """
        ToMBL tool. Used to push data to MBL using the Splunk Web API.
        :param config: configuration file
        """
        super().__init__(config, [AlertAction.get('All')])
        self._logger = logging.getLogger("LQMT.ToolName.{0}".format(self.getName()))
        self.alerts = {}
        self.sourcetype_lexicon = ['block', 'spearphish', 'malware']

        self._parser = FlexTransformParser({'mbl': 'resources/sampleConfigurations/MBL.cfg'})
        for file_type, source_config in self._config.source_configs.items():
            self._parser.add_parser(file_type, source_config)

            self.splunk_handler = ApiHandler(
                self._config.host,
                self._config.port,
                self._config.username,
                self._config.password,
                cert_check=self._config.cert_check,
                source=self._config.source,
                index=self._config.index,

            )

    def initialize(self):
        super().initialize()

    def process(self, alert, meta):
        """
        Process function. Handles the processing of data for the tool. 
        """
        # parse alert using custom parser
        mbl_alert = self._parser.custom_parser(alert, meta['PayloadFormat'], 'mbl')

        if mbl_alert:
            # pop alert data from list
            mbl_alert = mbl_alert.pop()

            # put alert data into a dictionary. key is generated from a hash of the list
            key_hash = self.compute_hash(str(mbl_alert))
            if key_hash not in self.alerts:
                self.alerts[key_hash] = mbl_alert

    def commit(self):
        """
        Commit function where the data is actually transmitted to Splunk instance. 
        """
        for dict_key, alert_data in self.alerts.items():
            sourcetype, message = self.parse_alert_dictionary(alert_data)

            # sourcetype override from user configuration
            if self._config.sourcetype:
                sourcetype = self._config.sourcetype

            # if sourcetype is valid, then send message
            if sourcetype in self.sourcetype_lexicon:
                self.splunk_handler.send_message(message, sourcetype=sourcetype)

    def cleanup(self):
        pass

    @staticmethod
    def parse_alert_dictionary(alert_data):
        """
        Method used for extracting the source type and message data from the provided alert data dictionary
        :param alert_data: dictionary containing parsed alert data
        :return: returns the sourcetype(str) and formatted message(str) both of which are derived from the alert_data
        dictionary
        """
        message = ""
        sourcetype = ""
        for alert_dictionary in alert_data:
            if 'sourcetype' in alert_dictionary:

                # Extract sourcetype from alert data and delete key from dictionary.
                sourcetype = alert_dictionary['sourcetype'].strip("'")
                del alert_dictionary['sourcetype']

            # format message in key value format. Replace single string with double quotes.
            for key, data in alert_dictionary.items():
                message += "{0}={1} ".format(key, str(data).replace("'", '"'))

        return sourcetype, message

    @staticmethod
    def compute_hash(string):
        """
        Method used for turning an alert string into a hash. Currently being used to sort out duplicate data.
        :param string: Alert data in of the type Str
        :return: returns sha256 digest of given string
        """
        return hashlib.sha256(string.encode('utf-8')).hexdigest()
