from lqmt.lqm.tool import Tool
import logging
from lqmt.lqm.data import AlertAction
import os


class ToCSV(Tool):
    def __init__(self, config):
        super().__init__(config, [AlertAction.get('All')])
        self._logger = logging.getLogger("LQMT.CSV.{0}".format(self.getName()))
        self._fp = None

    def initialize(self):
        super().initialize()
        self._fp = None

    def fileBegin(self):
        pass

    def fileDone(self):
        pass

    # Will only be called for alerts this tool can process
    def process(self, alert):
        if self._fp is None and not self._openFile():
            self.disable()
        if self.isEnabled():
            # write the alert to the file
            self._fp.write(",".join(alert.getFields(self._config.fields)) + "\n")
            self._fp.flush()
        return alert

    def commit(self):
        pass

    def cleanup(self):
        if self._fp is not None:
            self._fp.close()

    def _openFile(self):
        try:
            file = self._config.getFile()
            fileDirectory = os.path.dirname(file)
            if not os.path.exists(fileDirectory):
                os.makedirs(fileDirectory, 0o755, True)
            self._fp = open(file, 'a')
            self._fp.write(",".join(self._config.fields) + "\n")
            return True
        except Exception as e:
            self._logger.error("Unable to open csv file: {0}".format(file))
            self._logger.error(e)
            return False
