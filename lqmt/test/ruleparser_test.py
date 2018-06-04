import os
import time
import uuid
from unittest import TestCase, main
from lqmt.lqm.systemconfig import SystemConfig
from lqmt.lqm.parsers.RuleParser.parser import RuleParser
from lqmt.test.test_data.sample_inputs import SNORTEXAMPLE, YARAFILE


class TestRuleParser(TestCase):

    def setUp(self):
        sysconf = SystemConfig()
        self.sys_config = sysconf.getConfig()
        self.sys_config = self.sys_config['parsers']
        self.ruleparser = RuleParser()
        self.time = str(time.time()).split('.')[0]
        self.directory = os.path.dirname(__file__)
        self.test_file = self.directory + "/" + SNORTEXAMPLE
        self.yara_test_file = self.directory + "/" + YARAFILE

    def getMeta(self):
        """
        Method for generating metadata. Relatively static for now, but can be expanded to be randomized on each test run

        :return: Returns metadata in a dictionary
        """
        meta = {
            "PayloadFormat": 'SnortRules',
            "SendingSite": "Test Site",
            "PayloadType": "Alert",
            "UploadID": str(uuid.uuid4()).upper(),
            "FileName": "TestAlert",
            "SentTimestamp": self.time,
            "DownloadElementExtendedAttribute": [
                {
                    "Field": "Custodian",
                    "Value": "Test Custodian"
                },
                {
                    "Field": "Markings",
                    "Value": "TLP"
                },
                {
                    "Field": "Originator",
                    "Value": "Test Originator"
                },
                {
                    "Field": "Version",
                    "Value": "1.1.1"
                }
            ]
        }

        return meta

    def __default_config(self):
        # setup config context for test
        self.ruleparser._sources = []
        self.ruleparser._line_offset = 0
        self.ruleparser._rules = ['snort', 'yara']

    def test_rules_no_sources(self):
        # Test runs with no source filtering to confirm parsed
        self.__default_config()

        alerts = self.ruleparser.parse(self.test_file, self.getMeta())

        # confirm Parser filled all data variables, and found snort and yara rules
        self.assertIsNotNone(alerts)
        self.assertIsNotNone(alerts[0]._rules)
        self.assertIsNotNone(alerts[0]._rawfile)
        self.assertEquals(len(alerts[0]._rules['snort']), 4)

    def test_rules_source1(self):
        # Test - find Custodian
        self.__default_config()
        self.ruleparser._sources = ['Test Custodian']

        alerts = self.ruleparser.parse(self.test_file, self.getMeta())

        # confirm Parser filled all data variables, and found snort and yara rules
        self.assertIsNotNone(alerts)
        self.assertIsNotNone(alerts[0]._rules)
        self.assertIsNotNone(alerts[0]._rawfile)
        self.assertEquals(len(alerts[0]._rules['snort']), 4)

    def test_rules_source2(self):
        # Test - find Originator
        self.__default_config()
        self.ruleparser._sources = ['Test Originator']

        alerts = self.ruleparser.parse(self.test_file, self.getMeta())

        # confirm Parser filled all data variables, and found snort and yara rules
        self.assertIsNotNone(alerts)
        self.assertIsNotNone(alerts[0]._rules)
        self.assertIsNotNone(alerts[0]._rawfile)
        self.assertEquals(len(alerts[0]._rules['snort']), 4)

    def test_rules_source3(self):
        # Test - Source not found
        self.__default_config()
        self.ruleparser._sources = ['Not Found']

        alerts = self.ruleparser.parse(self.test_file, self.getMeta())

        # confirm Parser returned empty list
        self.assertEquals(alerts, [])

    def test_rules_source4(self):
        # Test - find multiple sources
        self.__default_config()
        self.ruleparser._sources = ['Test Originator', 'Not Found']

        alerts = self.ruleparser.parse(self.test_file, self.getMeta())

        # confirm Parser filled all data variables, and found snort and yara rules
        self.assertIsNotNone(alerts)
        self.assertIsNotNone(alerts[0]._rules)
        self.assertIsNotNone(alerts[0]._rawfile)
        self.assertEquals(len(alerts[0]._rules['snort']), 4)

    def test_snort_rules(self):
        # Test - confirm snort extraction
        self.__default_config()

        alerts = self.ruleparser.parse(self.test_file, self.getMeta())

        # confirm Parser filled all data variables, and found snort and yara rules
        self.assertIsNotNone(alerts)
        self.assertIsNotNone(alerts[0]._rules)
        self.assertIsNotNone(alerts[0]._rawfile)
        self.assertEquals(len(alerts[0]._rules['snort']), 4)
        self.assertEquals(alerts[0]._rules['snort'][0], 'alert tcp any any -> any any (msg:"FOX-SRT - Flowbit - TLS-SSL Client Hello"; flow:established; dsize:< 500; content:"|16 03|"; depth:2; byte_test:1, <=, 2, 3; byte_test:1, !=, 2, 1; content:"|01|"; offset:5; depth:1; content:"|03|"; offset:9; byte_test:1, <=, 3, 10; byte_test:1, !=, 2, 9; content:"|00 0f 00|"; flowbits:set,foxsslsession; flowbits:noalert; threshold:type limit, track by_src, count 1, seconds 60; reference:cve,2014-0160; classtype:bad-unknown; sid: 21001130; rev:9;)\n')
        self.assertEquals(alerts[0]._rules['snort'][1], 'alert tcp any any -> any any (msg:"FOX-SRT - Suspicious - TLS-SSL Large Heartbeat Response"; flow:established; flowbits:isset,foxsslsession; content:"|18 03|"; depth: 2; byte_test:1, <=, 3, 2; byte_test:1, !=, 2, 1; byte_test:2, >, 200, 3; threshold:type limit, track by_src, count 1, seconds 600; reference:cve,2014-0160; classtype:bad-unknown; sid: 21001131; rev:5;)\n')
        self.assertEquals(alerts[0]._rules['snort'][2], 'alert icmp any any -> any any (msg:"ICMP Packet"; sid:477; rev:3;)\n')
        self.assertEquals(alerts[0]._rules['snort'][3], 'alert tcp any 22 -> any any (msg:"SSH Test"; sid:488; rev:1;)\n')

    def test_snort_offset(self):
        # Test - confirm snort extraction at offset
        self.__default_config()
        self.ruleparser._line_offset = 2

        alerts = self.ruleparser.parse(self.test_file, self.getMeta())

        # confirm Parser filled all data variables, and found snort and yara rules
        self.assertIsNotNone(alerts)
        self.assertIsNotNone(alerts[0]._rules)
        self.assertIsNotNone(alerts[0]._rawfile)
        self.assertEquals(len(alerts[0]._rules['snort']), 2)
        self.assertEquals(alerts[0]._rules['snort'][0], 'alert icmp any any -> any any (msg:"ICMP Packet"; sid:477; rev:3;)\n')
        self.assertEquals(alerts[0]._rules['snort'][1], 'alert tcp any 22 -> any any (msg:"SSH Test"; sid:488; rev:1;)\n')

    def test_skip_snort(self):
        self.__default_config()
        self.ruleparser._rules = ['yara']

        alerts = self.ruleparser.parse(self.test_file, self.getMeta())

        self.assertEquals(alerts[0]._rules, {})

    def test_skip_yara(self):
        self.__default_config()
        self.ruleparser._rules = ['snort']
        meta = self.getMeta()
        meta['PayloadFormat'] = 'YaraRules'

        alerts = self.ruleparser.parse(self.yara_test_file, meta)

        self.assertEquals(alerts[0]._rules, {})

    def test_yara_rules(self):
        self.__default_config()
        meta = self.getMeta()
        meta['PayloadFormat'] = 'YaraRules'

        alerts = self.ruleparser.parse(self.yara_test_file, meta)

        self.assertIsNotNone(alerts)
        self.assertIsNotNone(alerts[0]._rules)
        self.assertIsNotNone(alerts[0]._rawfile)
        self.assertEquals(len(alerts[0]._rules['yara']), 1)


if __name__ == '__main__':
    main()
