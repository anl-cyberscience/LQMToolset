import os
import logging
import datetime
from lqmt.lqm.tool import ToolConfig


class BroConfig(ToolConfig):
    def __init__(self, configData, csvToolInfo, unhandledCSV):
        super().__init__(configData, csvToolInfo, unhandledCSV)
        self.logger = logging.getLogger("LQMT.ToBro.{0}".format(self.getName()))
        self.header_fields = self.validation('header_fields', list, default="all")
        self.file = self.validation('file', str, default="./lqmt-bro-feed.txt")
        self.increment_file = self.validation('increment_file', bool, default=False)
        self.null_value = self.validation('null_value', str, default='-')

        if self.increment_file:
            base, extension = os.path.splitext(self.file)
            file_name = "."+datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
            self.file = base + file_name + extension
