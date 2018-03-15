import logging
from lqmt.lqm.tool import ToolConfig


class SnortConfig(ToolConfig):
    """
    Configuration class for Snort Tool
    """

    def __init__(self, configData, snortToolInfo, unhandledCSV):
        """
        Constructor
        :param configData:
        :param snortToolInfo:
        :param unhandledCSV:
        """
        super().__init__(configData, snortToolInfo, unhandledCSV)
        self.logger = logging.getLogger("LQMT.ToSnort.{0}".format(self.getName()))

        self.snort_cfg_filepaths = self.validation('config_paths', list, required=True, default=['/etc/nsm'])
        self.snort_cfg_filename = self.validation('config_filename', str, default='snort.conf')
        self.rule_paths = self.validation('rule_paths', list, required=True, default=['/etc/nsm/rules'])
        self.rule_filename = self.validation('rule_filename', str, default='stix.rules')
        self.max_rules = self.validation('max_rules_count', int, default=-1)