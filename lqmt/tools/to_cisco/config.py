import logging
from lqmt.lqm.tool import ToolConfig

class CiscoConfig(ToolConfig):
    """
    ToCisco tool configuration. Pulls configuration data from user config file
    and validates it.
    """
    def __init__(self, configData, csvToolInfo, unhandledCSV):
        super().__init__(configData, csvToolInfo, unhandledCSV)
        self.logger = logging.getLogger("LQMT.ToCisco.{}".format(self.getName()))

        self.host = self.validation('host', str, required=True)
        self.username = self.validation('username', str, required=True)
        self.password = self.validation('password', str, required=True)
        self.verify_cert = self.validation('verify_cert', str, default=True)
