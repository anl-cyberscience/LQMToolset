import logging
from lqmt.lqm.tool import ToolConfig


class FromMBLConfig(ToolConfig):
    def __init__(self, configData, csvToolInfo, unhandledCSV):
        super().__init__(configData, csvToolInfo, unhandledCSV)
        self.logger = logging.getLogger("LQMT.ToolName.{0}".format(self.getName()))

        self.host = self.validation('host', str, required=True)
        self.port = self.validation('port', int, default=8089)
        self.username = self.validation('username', str, required=True)
        self.password = self.validation('password', str, required=True)
        self.cert_check = self.validation('cert_check', bool, default=True)
        self.source = self.validation('source', str, default="")
        self.sourcetype = self.validation('sourcetype', str, default="")
        self.index = self.validation('index', str)
        self.output_mode = self.validation('output_mode', str, default="CSV")
        # TODO: Give user the option to use the the source_dir as the output dir. Possibly if this var is empty?
        self.output_directory = self.validation('output_directory', str)
        self.timeout_duration = self.validation('timeout_duration', int, default=15)
        self.splunk_query = self.validation('splunk_query', str, required=True)
