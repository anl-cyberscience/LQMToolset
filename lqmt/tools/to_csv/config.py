from lqmt.lqm.tool import ToolConfig
from lqmt.lqm.exceptions import ConfigurationError
from lqmt.lqm.data import Alert
import logging
import os
import datetime


class CSVConfig(ToolConfig):
    def __init__(self, configData, csvToolInfo, unhandledCSV):
        super().__init__(configData, csvToolInfo, unhandledCSV)
        self.logger = logging.getLogger("LQMT.CSV.{0}".format(self.getName()))

        self._file = self.validation('file', str, required=True)
        self.fields = self.validation('fields', list, required=True)

        # Additional checks:
        invalid = self._initFields(self.fields)
        if invalid:
            raise ConfigurationError("Invalid alert field(s) provided. Invalid field(s): {0}".format(','.join(invalid)))

        # File incrementing. Make this an option rather then a default. See to_bro or to_flextext tools
        base, extension = os.path.splitext(self._file)
        file_name = "." + datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        self._file = base + file_name + extension

    def getFile(self):
        return self._file

    def _initFields(self, fields):
        invalid = []
        for fld in fields:
            if not Alert.isValidField(fld):
                invalid.append(fld)

        return invalid

    def getFields(self):
        return self.fields
