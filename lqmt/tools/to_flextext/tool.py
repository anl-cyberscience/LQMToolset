import os
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
        self._file_obj = None
        self._processed = []

    def initialize(self):
        super().initialize()

    def process(self, datafile, meta):
        """
        Process function. Handles the processing of data for the tool. Does so by calling the FlexText parser

        :param datafile: String that contains the path to the alert being processed.
        :param meta: meta data of the datafile. Used to assign correct parser
        """
        if self._file_obj is None and not self.openfile():
            self.disable()
        if self.isEnabled():
            if datafile not in self._processed:
                # Use flextext parser to parse datafile.
                self._parser.parseflextext(datafile, meta, self._file_obj, self._config.config_to_str())
                self._processed.append(datafile)

    def openfile(self):
        try:
            file = self._config.file_destination
            file_dir = os.path.dirname(file)
            if not os.path.exists(file_dir):
                os.makedirs(file_dir, 0o755, True)
            self._file_obj = open(file, 'a')
            return True
        except Exception as e:
            self._logger.error("Unable to open csv file: {0}".format(file))
            self._logger.error(e)
            return False

    def commit(self):
        pass

    def cleanup(self):
        if self._file_obj is not None:
            self._file_obj.close()
