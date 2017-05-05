import logging
from lqmt.lqm.tool import EgressTool
from lqmt.lqm.data import AlertAction


class FromMBL(EgressTool):
    def __init__(self, config):
        """
        ToToolName description
        :param config: configuration file
        """
        super().__init__(config)
        print('Init function of FromMBL Tool')
        self._logger = logging.getLogger("LQMT.ToolName.{0}".format(self.getName()))

    def initialize(self):
        print("Initialize function of FormMBL Tool")
        # super().initialize()

    def process(self, alert):
        """
        Process function. Handles the processing of data for the tool. 
        """
        print("Process function of FromMBL Tool")

    def commit(self):
        print("Commit function of FromMBL Tool")


    def cleanup(self):
        print("Cleanup function of FromMBL Tool")
