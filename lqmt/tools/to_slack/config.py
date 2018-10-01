import logging
from lqmt.lqm.tool import ToolConfig


class SlackConfig(ToolConfig):
    """
    Configuration class for Slack Tool
    """

    def __init__(self, config_data, slack_tool_info, unhandled_csv):
        """
        Constructor
        :param config_data:
        :param slack_tool_info:
        :param unhandled_csv:
        """
        super().__init__(config_data, slack_tool_info, unhandled_csv)
        self.logger = logging.getLogger('LQMT.ToSlack.{}'.format(self.getName()))

        self.token = self.validation('token', str, required=True)
        self.channels = self.validation('channels', list, required=True)
        self.title = self.validation('post_title', str, required=True, default='File Upload')
        self.body = self.validation('post_body', str, required=False)
