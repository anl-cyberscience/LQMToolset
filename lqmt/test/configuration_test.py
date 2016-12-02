import os
import toml
from unittest import TestCase, main
from lqmt.lqm.tool import ToolConfig
from lqmt.lqm.config import LQMToolConfig
from lqmt.lqm.systemconfig import SystemConfig
from lqmt.test.test_data.sample_config import USERCONFIG


class TestConfiguration(TestCase):
    """
    Testing class for the configuration components
    """

    def setUp(self):
        """
        Initialize the system configuration and the user configuration.

        Note the forward slash replacements for the user configuration. This is due to the forward slash being a
        restricted character in TOML(package used to parse configuration files in LQMT).
        """
        # relative pathing variables. Replace function calls for Windows compatibility.
        self.directory = os.path.dirname(__file__)
        self.alerts = self.directory + "/test_data/"
        self.alerts = self.alerts.replace("\\", "/")
        self.logging = self.directory + "/test_data/test-logs/lqmt"
        self.logging = self.logging.replace("\\", "/")
        self.whitelist = self.directory + "/test_data/whitelist/whitelist.txt"
        self.whitelist = self.whitelist.replace("\\", "/")
        self.whitelist_db = self.directory + "/test_data/whitelist/whitelist.db"
        self.whitelist_db = self.whitelist_db.replace("\\", "/")

        # configurations initialized
        sysconf = SystemConfig()
        self.sys_config = sysconf.getConfig()
        config = USERCONFIG.format(self.alerts, self.logging, self.whitelist, self.whitelist_db)
        self.toml_config = toml.loads(config)
        self.toml_config = self.toml_config["Tools"]["FlexText"][0]  # dirty way of parsing userconfig for ToolConfig
        self.user_config = LQMToolConfig(config)
        self.toolConfig = ToolConfig(self.toml_config, csvToolInfo={""}, unhandledCSV={""})

    def test_user_sources(self):
        """
        Note the replace call. The alert path was replaced with 4 slashes above due to a TOML restriction. After TOML
        parses the config defined above, it strips the extra slashes. We have to do that with our non-stripped alerts
        variable
        """
        sources = self.user_config.getSources().pop()
        self.assertEquals(sources._dirs, [self.alerts.replace("\\\\", "\\")])
        self.assertIsNone(sources.files_to_process)

    def test_user_whitelist(self):
        whitelist = self.user_config.getWhitelist()
        self.assertIsNotNone(whitelist)
        self.assertEqual(whitelist.whitelistFile, self.whitelist.replace("\\\\", "\\"))
        self.assertEqual(whitelist.db, self.whitelist_db.replace("\\\\", "\\"))

    def test_user_parsers(self):
        self.assertIsNotNone(self.user_config.getParser('Cfm13Alert'))
        self.assertIsNotNone(self.user_config.getParser('Cfm20Alert'))
        self.assertIsNotNone(self.user_config.getParser('stix-tlp'))

    def test_user_toollist(self):
        self.assertEqual(self.user_config.getToolsList(), ['FlexText'])

    def test_user_toolchain(self):
        toolchain = self.user_config.getToolChains().pop()
        self.assertEquals(toolchain._name, "anl-flextext-test")
        self.assertEquals(len(toolchain._tools), 1)

    def test_validation(self):
        self.assertTrue(self.toolConfig.validation('incrementFile', bool))
        self.assertEquals(self.toolConfig.validation('fileParser', str, required=True, default="CSV"), 'CSV')
        self.assertEquals(
            self.toolConfig.validation('fields', str, required=True),
            "indicator,reportedTime,detectedTime,duration1,priors,directSource,reason1,majorTags,sensitivity,"
            "reconAllowed,restriction"
        )


if __name__ == '__main__':
    main()
