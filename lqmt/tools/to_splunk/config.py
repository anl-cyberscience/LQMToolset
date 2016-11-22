import logging
from lqmt.lqm.tool import ToolConfig


class SplunkConfig(ToolConfig):

    def __init__(self, configData, csvToolInfo, unhandledCSV):
        super().__init__(configData, csvToolInfo, unhandledCSV)
        self.logger = logging.getLogger("LQMT.Splunk.{0}".format(self.getName()))

        self.host = self.validation('host', str, required=True)
        self.port = self.validation('port', int, default=8089)
        self.username = self.validation('username', str, required=True)
        self.password = self.validation('password', str, required=True)
        self.cert_check = self.validation('cert_check', bool, default=True)
        self.source = self.validation('source', str, default="lqmt")
        self.sourcetype = self.validation('sourcetype', str, required=True)
