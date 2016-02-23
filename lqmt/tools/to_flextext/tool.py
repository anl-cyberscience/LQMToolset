import logging
from lqmt.lqm.data import AlertAction
from lqmt.lqm.tool import Tool
from lqmt.lqm.parsers.FlexTransform.parser import FlexTransformParser


class ToFlexText(Tool):
    def __init__(self, config):
        """
        ToFlexText tool. Used to reformat CTI data in a user configured manner.

        :param config: configuration file
        """
        super().__init__(config, [AlertAction.get('All')])
        self._logger = logging.getLogger("LQMT.FlexText.{0}".format(self.getName()))

        # format parserConfig dict and then initialized parser
        parserconfig = {'Cfm13Alert': self._config.cfm13_config, 'CSV': self._config.flext_config}
        self._parser = FlexTransformParser(parserconfig)

    def initialize(self):
        super().initialize()

    def process(self, datafile, meta):
        """
        Process function. Handles the processing of data for the tool. Does so by calling the FlexText parser

        :param datafile: String that contains the path to the alert being processed.
        """

        self._parser.parseflextext(datafile, meta, self._config.file_destination, self._config.config_to_str())

    def commit(self):
        pass

    def cleanup(self):
        pass
