import os
import time
import uuid
from unittest import TestCase, main
from lqmt.lqm.parsers.STIXParser.parser import STIXParser
from lqmt.lqm.systemconfig import SystemConfig
from lqmt.test.test_data.sample_inputs import STIXRULES, YARAEXAMPLE


class TestSTIXParser(TestCase):

    def setUp(self):
        sysconf = SystemConfig()
        self.sys_config = sysconf.getConfig()
        self.sys_config = self.sys_config['parsers']
        self.stixparser = STIXParser()
        self.time = str(time.time()).split('.')[0]
        self.directory = os.path.dirname(__file__)
        self.test_file = self.directory + "/" + STIXRULES

    def getMeta(self):
        """
        Method for generating metadata. Relatively static for now, but can be expanded to be randomized on each test run

        :return: Returns metadata in a dictionary
        """
        meta = {
            "PayloadFormat": 'STIX',
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
        self.stixparser._sources = []
        self.stixparser._elements = ['indicators']
        self.stixparser._rules = ['snort', 'yara']

    def test_stix_no_sources(self):
        # Test runs with no source filtering to confirm parsed
        self.__default_config()

        alerts = self.stixparser.parse(self.test_file, self.getMeta())

        # confirm Parser filled all data variables, and found snort and yara rules
        self.assertIsNotNone(alerts)
        self.assertIsNotNone(alerts[0]._stix_elements)
        self.assertIsNotNone(alerts[0]._full_rules)
        self.assertIsNotNone(alerts[0]._rawfile)
        self.assertEquals(len(alerts[0]._stix_elements[0]), 2)

    def test_stix_source1(self):
        # Test - find Information_Source
        self.__default_config()
        self.stixparser._sources = ['Test Source']

        alerts = self.stixparser.parse(self.test_file, self.getMeta())

        # confirm Parser filled all data variables, and found snort and yara rules
        self.assertIsNotNone(alerts)
        self.assertIsNotNone(alerts[0]._stix_elements)
        self.assertIsNotNone(alerts[0]._full_rules)
        self.assertIsNotNone(alerts[0]._rawfile)
        self.assertEquals(len(alerts[0]._stix_elements[0]), 2)

    def test_stix_source2(self):
        # Test - find Custodian
        self.__default_config()
        self.stixparser._sources = ['Test Custodian']

        alerts = self.stixparser.parse(self.test_file, self.getMeta())

        # confirm Parser filled all data variables, and found snort and yara rules
        self.assertIsNotNone(alerts)
        self.assertIsNotNone(alerts[0]._stix_elements)
        self.assertIsNotNone(alerts[0]._full_rules)
        self.assertIsNotNone(alerts[0]._rawfile)
        self.assertEquals(len(alerts[0]._stix_elements[0]), 2)

    def test_stix_source3(self):
        # Test - find Originator
        self.__default_config()
        self.stixparser._sources = ['Test Originator']

        alerts = self.stixparser.parse(self.test_file, self.getMeta())

        # confirm Parser filled all data variables, and found snort and yara rules
        self.assertIsNotNone(alerts)
        self.assertIsNotNone(alerts[0]._stix_elements)
        self.assertIsNotNone(alerts[0]._full_rules)
        self.assertIsNotNone(alerts[0]._rawfile)
        self.assertEquals(len(alerts[0]._stix_elements[0]), 2)

    def test_stix_source4(self):
        # Test - Source not found
        self.__default_config()
        self.stixparser._sources = ['Not Found']

        alerts = self.stixparser.parse(self.test_file, self.getMeta())

        # confirm Parser returned empty list
        self.assertEquals(alerts, [])

    def test_stix_source5(self):
        # Test - find multiple sources
        self.__default_config()
        self.stixparser._sources = ['Test Originator', 'Not Found']

        alerts = self.stixparser.parse(self.test_file, self.getMeta())

        # confirm Parser filled all data variables, and found snort and yara rules
        self.assertIsNotNone(alerts)
        self.assertIsNotNone(alerts[0]._stix_elements)
        self.assertIsNotNone(alerts[0]._full_rules)
        self.assertIsNotNone(alerts[0]._rawfile)
        self.assertEquals(len(alerts[0]._stix_elements[0]), 2)

    def test_stix_elements1(self):
        # Test - find Originator
        self.__default_config()
        self.stixparser._elements = ['StIx_header', 'Indicators']

        alerts = self.stixparser.parse(self.test_file, self.getMeta())

        # confirm Parser filled all data variables, and found snort and yara rules
        self.assertIsNotNone(alerts)
        self.assertIsNotNone(alerts[0]._stix_elements)
        self.assertEquals(len(alerts[0]._stix_elements), 2)

    def test_empty_rules(self):
        self.__default_config()
        self.stixparser._elements = []
        self.stixparser._rules = []

        alerts = self.stixparser.parse(self.test_file, self.getMeta())

        # ensure empty full context & empty rules dict
        self.assertEquals(alerts[0]._rules, {})
        self.assertEquals(alerts[0]._full_rules, [])

    def test_snort_rules(self):
        self.__default_config()
        self.stixparser._elements = []
        self.stixparser._rules = ['snort']

        alerts = self.stixparser.parse(self.test_file, self.getMeta())

        self.assertEquals(len(alerts[0]._rules['snort']), 2)  # snort entry size 2
        self.assertEquals(alerts[0]._rules['snort'][0], 'alert tcp any any -> any any (msg:"FOX-SRT - Flowbit - TLS-SSL Client Hello"; flow:established; dsize:< 500; content:"|16 03|"; depth:2; byte_test:1, <=, 2, 3; byte_test:1, !=, 2, 1; content:"|01|"; offset:5; depth:1; content:"|03|"; offset:9; byte_test:1, <=, 3, 10; byte_test:1, !=, 2, 9; content:"|00 0f 00|"; flowbits:set,foxsslsession; flowbits:noalert; threshold:type limit, track by_src, count 1, seconds 60; reference:cve,2014-0160; classtype:bad-unknown; sid: 21001130; rev:9;)')
        self.assertEquals(alerts[0]._rules['snort'][1], 'alert tcp any any -> any any (msg:"FOX-SRT - Suspicious - TLS-SSL Large Heartbeat Response"; flow:established; flowbits:isset,foxsslsession; content:"|18 03|"; depth: 2; byte_test:1, <=, 3, 2; byte_test:1, !=, 2, 1; byte_test:2, >, 200, 3; threshold:type limit, track by_src, count 1, seconds 600; reference:cve,2014-0160; classtype:bad-unknown; sid: 21001131; rev:5;)')
        self.assertNotIn('yara', alerts[0]._rules)  # yara entry is empty

    def test_yara_rules(self):
        self.__default_config()
        self.stixparser._elements = []
        self.stixparser._rules = ['yara']

        alerts = self.stixparser.parse(self.test_file, self.getMeta())

        self.assertEquals(len(alerts[0]._rules['yara']), 1)  # snort entry size 2
        self.assertEquals(alerts[0]._rules['yara'][0], YARAEXAMPLE)
        self.assertNotIn('snort', alerts[0]._rules)  # yara entry is empty

    def test_full_context(self):
        self.__default_config()
        self.stixparser._elements = []

        alerts = self.stixparser.parse(self.test_file, self.getMeta())

        # if xsi:type is in the entry, it grabbed the full context
        self.assertEquals(len(alerts[0]._full_rules), 2)
        self.assertEquals(alerts[0]._full_rules[0]['xsi:type'], 'snortTM:SnortTestMechanismType')
        self.assertEquals(alerts[0]._full_rules[1]['xsi:type'], 'yaraTM:YaraTestMechanismType')


if __name__ == '__main__':
    main()
