import logging
from lqmt.lqm.tool import ToolConfig


class MetaMakerConfig(ToolConfig):
    def __init__(self, config, csvToolInfo, unhandledCSV):
        super().__init__(config, csvToolInfo, unhandledCSV)
        self.logger = logging.getLogger("LQMT.Splunk.{0}".format(self.getName()))

        self.path = self.validation('path', str, required=True)
        self.format = self.validation('format', str, required=True)
        self.type = self.validation('type', str, default="Alert")
        self.site = self.validation('site', str, required=True)
        self.sensitivity = self.validation('sensitivity', str, default="noSensitivity")
        self.recon = self.validation('recon', str, default="Touch")
        self.restrictions = self.validation('restrictions', str, default="white")
