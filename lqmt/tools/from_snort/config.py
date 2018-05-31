import logging
from lqmt.lqm.tool import ToolConfig


class FromSnortConfig(ToolConfig):
    def __init__(self, configData, csvToolInfo, unhandledCSV):
        super().__init__(configData, csvToolInfo, unhandledCSV)
        self.logger = logging.getLogger("LQMT.ToolName.{0}".format(self.getName()))

        modes = ['full', 'match']

        self.alert_paths = self.validation('alert_paths', list, required=True, default=['/var/log/snort/alert'])
        self.packets_paths = self.validation('packet_paths', list, required=True, default=['/nsm/sensor_data'])
        self.mode = self.validation('mode', str, default='full')
        if self.mode not in modes:
            self.mode = 'full'
        self.data_age = self.validation('max_file_age', str, required=True, default='5 minutes')
        self.rule_list = self.validation('rules', list, required=True, default=['/etc/nsm/rules/downloaded.rules'])
        self.result_path = self.validation('result_path', str, required=True, default='lqmt/results')
        # TODO: For now do not enable returning these snort context information
        # self.config_paths = self.validation('config_paths', list, default=['/etc/nsm'])
        # self.rules_paths = self.validation('rule_paths', list, default=['/etc/nsm/rules'])
        # self.tblsht_paths = self.validation('troubleshooting_paths', list, default=['/var/log/nsm'])
        # self.logs_paths = self.validation('log_paths', list, default=['/var/log/nsm'])
