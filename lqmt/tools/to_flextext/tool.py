import os
import logging
import csv
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
        """
        Creates and opens the file specified in the user configuration, specifically the file_destination variable.
        The file object create here is then passed to the parser
        """
        try:
            file = self._config.file_destination
            file_dir = os.path.dirname(file)
            if not os.path.exists(file_dir):
                os.makedirs(file_dir, 0o755, True)
            self._file_obj = open(file, 'a')
            self.writeheader()
            return True
        except Exception as e:
            self._logger.error("Unable to open csv file: {0}".format(self._config.file_destination))
            self._logger.error(e)
            return False

    def writeheader(self):
        """
        When inserting the header using FlexT, the header gets repeated everytime a file is processed due to the way the
        config is currently sent over. This (hacky) solution writes the header to the file before any configuration data
        is sent over to FlexT. After the header is written the header_line value is set to False so that the header
        isn't rewritten when the configuration is passed to FlexT.
        """

        if self._config.header_line:
            quote_style = None
            if self._config.quote_style.lower() == 'none':
                quote_style = csv.QUOTE_NONE
            elif self._config.quote_style.lower() == 'nonnumeric':
                quote_style = csv.QUOTE_NONNUMERIC
            elif self._config.quote_style.lower() == 'all':
                quote_style = csv.QUOTE_ALL
            elif self._config.quote_style.lower() == 'minimal':
                quote_style = csv.QUOTE_MINIMAL

            csv.register_dialect('flext',
                                 delimiter=self._config.delimiter,
                                 quotechar=self._config.quote_char,
                                 escapechar=bytes(self._config.escape_char, "utf-8").decode("unicode_escape"),
                                 doublequote=self._config.double_quote,
                                 lineterminator='\r\n',
                                 quoting=quote_style
                                 )

            writer = csv.DictWriter(self._file_obj, self._config.fields.split(','), dialect='flext')

            writer.writeheader()
            self._config.header_line = False

    def commit(self):
        pass

    def cleanup(self):
        if self._file_obj is not None:
            self._file_obj.close()
