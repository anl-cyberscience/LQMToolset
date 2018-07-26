"""
Created on July 26, 2018

@author: grjohnson
"""
import logging
from lqmt.lqm.tool import ToolConfig


class FromMattermostConfig(ToolConfig):
    def __init__(self, configData, csvToolInfo, unhandledCSV):
        super().__init__(configData, csvToolInfo, unhandledCSV)
        self.logger = logging.getLogger("LQMT.ToolName.{0}".format(self.getName()))

        self.result_path = self.validation('result_path', str, required=True, default='lqmt/results')
