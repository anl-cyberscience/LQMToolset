from lqmt.lqm.tool import ToolConfig
from lqmt.lqm.exceptions import ConfigurationError
from lqmt.lqm.data import Alert
import logging
import os
import datetime


class CSVConfig(ToolConfig):
    def __init__(self, configData, csvToolInfo, unhandledCSV):
        super().__init__(configData, csvToolInfo, unhandledCSV)
        self._logger = logging.getLogger("LQMT.CSV.{0}".format(self.getName()))
        self.fields = ""

        hasError = False
        self._file = None
        if 'file' in configData:
            file = configData['file']
            filebase, fext = os.path.splitext(file)
            tss = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
            self._file = filebase + "." + tss + fext
        else:
            hasError = True
            self._logger.error("'file' must be specified for CSV tool")

        if 'fields' in configData:
            invalid = self._initFields(configData['fields'])
            if not invalid:
                self.fields = configData['fields']
            else:
                hasError = True
                plural = ""
                if len(invalid) > 1:
                    plural = "s"
                self._logger.error("Invalid alert field{0} specified: {1}.".format(plural, ",".join(invalid)))
        else:
            self._logger.error("fields must be specified in the configuration")
            hasError = True

        if hasError:
            self.disable()
            raise ConfigurationError("Missing a required value in the user configuration for the to_csv tool")

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
