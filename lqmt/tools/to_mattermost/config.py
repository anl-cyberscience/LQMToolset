"""
Created on July 26, 2018

@author: grjohnson
"""
import logging
from lqmt.lqm.tool import ToolConfig


class MattermostConfig(ToolConfig):
    """
    Configuration class for Mattermost Tool
    """

    def __init__(self, configData, mmToolInfo, unhandledCSV):
        """
        Constructor
        :param configData:
        :param mmToolInfo:
        :param unhandledCSV:
        """
        super().__init__(configData, mmToolInfo, unhandledCSV)
        self.logger = logging.getLogger("LQMT.ToMattermost.{0}".format(self.getName()))
