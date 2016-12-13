import logging
from lqmt.lqm.tool import ToolConfig


class BroConfig(ToolConfig):
    def __init__(self, configData, csvToolInfo, unhandledCSV):
        super().__init__(configData, csvToolInfo, unhandledCSV)
        self.logger = logging.getLogger("LQMT.ToBro.{0}".format(self.getName()))
        self.fields = self.validation('fields', str, default="all")
        self.file = self.validation('file', str, default="./lqmt-bro-feed.txt")
        self.enumerate = self.validation('enumerate', bool, default=False)
        self.null_value = self.validation('null_value', str, default='-')
