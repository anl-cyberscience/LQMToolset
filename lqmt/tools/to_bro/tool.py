import logging
import os
import csv
from lqmt.lqm.tool import Tool
from lqmt.lqm.data import AlertAction
from lqmt.lqm.data import AlertFields


def replace_empty(value, replace):
    """
    Checks if value is a string and if it is empty. IF true, it's replaced with the provided value. Otherwise, the
    original value is returned
    :param value: Value to check
    :param replace: Value to replace empty string with
    """
    if isinstance(value, str) and not value:
        return replace
    else:
        return value


class ToBro(Tool):
    def __init__(self, config):
        """
        ToFlexText tool. Used to reformat CTI data in a user configured manner.
        :param config: configuration file
        """
        super().__init__(config, [AlertAction.get('All')])
        self._logger = logging.getLogger("LQMT.ToBro.{0}".format(self.getName()))
        self.file = None
        self.writer = None
        self.header_exists = False
        self.header_keys = list(AlertFields().fields.keys())
        self.header_keys.sort()

    def initialize(self):
        super().initialize()

    def process(self, alert):
        """
        Process function. Handles the processing of data for the tool. 
        """
        self.openfile()
        self.start_writer()

        # turn alert data into a csv row and replace empty values with user defined null value (defaults to hyphen)
        row = alert.getFields(self.header_keys)
        row = [replace_empty(c, self._config.null_value) for c in row]

        # write to file
        self.writer.writerow(row)

    def openfile(self):
        """
        Creates and opens the file specified in the user configuration, specifically the file_destination variable.
        """
        if self.file is None:
            try:
                file = self._config.file
                file_dir = os.path.dirname(file)
                if not os.path.exists(file_dir):
                    os.makedirs(file_dir, 0o755, True)
                if not os.path.exists(file):
                    open(file, 'w').close()
            except Exception as e:
                self._logger.error("Unable to open csv file: {0}".format(self._config.file_destination))
                self._logger.error(e)

            # create header and open file
            self.bro_header()
            self.file = open(file, 'a')

    def start_writer(self):
        if self.writer is None and self.file is not None:
            self.writer = csv.writer(self.file, delimiter='\t', quotechar="'")

    def bro_header(self):
        """
        Function that checks file for header. If the file doesn't exist it is created. If the file exists, and there
        is no header, the header is written. Bro's inteligence framework format specifies headers by having the first
        line in the file be '#fields' followed by user defined fields.
        """
        with open(self._config.file, 'r+') as f:
            if "#fields" not in f.readline():
                writer = csv.writer(f, delimiter='\t')
                writer.writerow(["#fields"] + self.header_keys)

    def commit(self):
        pass

    def cleanup(self):
        pass
