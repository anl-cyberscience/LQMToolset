import logging
from lqm.data import AlertAction
from lqm.tool import Tool


class ToFlexText(Tool):
    def __init__(self, config):
        Tool.__init__(self, config, [AlertAction.get('All')])
        self._logger = logging.getLogger("LQMT.FlexText.{0}".format(self.getName()))
        self._totalSent = 0

    def initialize(self):
        super().initialize()

    def process(self, data):
        pass

    def commit(self):
        pass

    def cleanup(self):
        pass