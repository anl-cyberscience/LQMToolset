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

        self.scheme = self.validation('scheme', str, required=False, default='https')
        self.url = self.validation('url', str, required=True)
        self.port = int(self.validation('port', str, required=False, default='8056'))
        self.login = self.validation('login', str, required=True)
        self.password = self.validation('password', str, required=True)
        self.channel_id = self.validation('channel_id', str, required=True)
