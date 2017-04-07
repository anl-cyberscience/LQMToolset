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
        print('in from tool')
        self._logger = logging.getLogger("LQMT.ToolName.{0}".format(self.getName()))

    def initialize(self):
        pass
        # super().initialize()

    def process(self, alert):
        """
        Process function. Handles the processing of data for the tool. 
        """
        pass

    def commit(self):
        pass

    def cleanup(self):
        pass
