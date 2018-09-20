"""
Created on Sept 7, 2018

@author: mghenderson
"""
import logging
from lqmt.lqm.tool import ToolConfig


class EmailConfig(ToolConfig):
    """
    Configuration class for Email Tool
    """

    def __init__(self, config_data, email_tool_info, unhandled_csv):
        """
        Constructor
        :param config_data:
        :param email_tool_info:
        :param unhandled_csv:
        """
        super().__init__(config_data, email_tool_info, unhandled_csv)
        self.logger = logging.getLevelName("LQMT.ToEmail.{}".format(self.getName()))

        self.outgoing_host = self.validation('outgoing_host', str, required=True)
        self.outgoing_port = self.validation('port', int, default=0)
        self.sender = self.validation('sender', str, required=True)
        self.recipients = self.validation('recipients', list, required=True)
        self.subject = self.validation('subject', str, required=True)
        self.body = self.validation('body', str, default=None)
