import logging
from lqmt.lqm.tool import Tool
from lqmt.lqm.data import AlertAction

class ToCisco(Tool):
    def __init__(self, config):
        """
        ToCisco Tool. Used to push data to Cisco ASA devices.

        :param config: configuration file
        """
        super().__init__(config, [AlertAction.get('All')])
        self._logger = logging.getLogger("LQMT.ToCisco.{0}".format(self.getName))

    def initialize(self):
        super().initialize()

    def process(self, alert):
        """
        Process function that handles the processing of data for the tool
        """
        pass

    def commit(self):
        pass

    def cleanup(self):
        pass
