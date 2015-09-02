from lqmt.lqm.tool import Tool
import logging
from lqmt.lqm.data import AlertAction
import os

class ToCSV(Tool):


    def __init__(self, config):
        Tool.__init__(self, config,[AlertAction.get('All')])
        self._logger = logging.getLogger("LQMT.CSV.{0}".format(self.getName()))
        self._fp=None

    def initialize(self):
        super().initialize()
        self._fp=None

    def fileBegin(self):
        pass

    def fileDone(self):
        pass

    #Will only be called for alerts this tool can process
    def process(self, alert):
        if(self._fp==None):
            if(not self._openFile()):
                self.disable()
        if(self.isEnabled()):
            # write the alert to the file
            self._fp.write(",".join(alert.getFields(self.getConfig().getFields()))+"\n")
            self._fp.flush()
        return alert
    
    def commit(self):
        pass

    def cleanup(self):
        self._fp.close()

    def _openFile(self):
        try:
            file = self.getConfig().getFile()
            d=os.path.dirname(file)
            if(not os.path.exists(d)):
                os.makedirs(d, 0o755, True)
            self._fp=open(file,'a')
            self._fp.write(",".join(self.getConfig().getFields())+"\n")
            return True
        except Exception as e:
            self._logger.error("Unable to open csv file: {0}".format(file))
            self._logger.error(e)
            return False
