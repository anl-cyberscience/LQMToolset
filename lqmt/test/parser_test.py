from unittest import TestCase, main
from lqmt.lqm.parsers.FlexTransform.parser import FlexTransformParser
from lqmt.lqm.systemconfig import SystemConfig
from lqmt.test.test_data.sample_inputs import CFM13ALERT, CFM20ALERT, STIX
import io
import time
import uuid


class TestParser(TestCase):
    """
    Testing class for the parser alert parser.
    """

    def setUp(self):
        sysconf = SystemConfig()
        self.sys_config = sysconf.getConfig()
        self.sys_config = self.sys_config['parsers']
        self.flext = FlexTransformParser()

        # Add parsers for the different data formats
        self.flext.add_parser('LQMTools', 'resources/sampleConfigurations/lqmtools.cfg')
        self.flext.add_parser('Cfm13Alert', 'resources/sampleConfigurations/cfm13.cfg')
        self.flext.add_parser('Cfm20Alert', 'resources/sampleConfigurations/cfm20alert.cfg')
        self.flext.add_parser('stixtlp', 'resources/sampleConfigurations/stix_tlp.cfg')
        self.flext.add_parser('STIX', 'resources/sampleConfigurations/stix_tlp.cfg')

        # Standard timestamp that can be used so all meta files use the same time and for easier validation
        self.time = str(time.time()).split('.')[0]

        # Parse all the data ahead of the tests
        self.cfm13_parsed_data = self.flext.parse(io.StringIO(CFM13ALERT), self.getMeta("Cfm13Alert"))
        self.cfm20_parsed_data = self.flext.parse(io.StringIO(CFM20ALERT), self.getMeta("Cfm20Alert"))
        self.stix_parsed_data = self.flext.parse(io.StringIO(STIX), self.getMeta("STIX"))

    def getMeta(self, payloadFormat):
        """
        Method for generating metadata. Relatively static for now, but can be expanded to be randomized on each test run

        :param payloadFormat: Expected format of the payload.
        :return: Returns metadata in a dictionary
        """
        meta = {
            "PayloadFormat": payloadFormat,
            "SendingSite": "ANL",
            "PayloadType": "Alert",
            "UploadID": str(uuid.uuid4()).upper(),
            "FileName": "TestAlert",
            "SentTimestamp": self.time,
        }

        return meta

    # CFM13 format tests
    def test_cfm13_content_returned(self):
        self.assertEquals(len(self.cfm13_parsed_data), 1)

    def test_cfm13_indicator(self):
        self.assertEquals(self.cfm13_parsed_data[0]._indicator, "10.10.10.10")

    def test_cfm13_indicator_type(self):
        self.assertEquals(self.cfm13_parsed_data[0]._indicatorType, "IPv4Address")

    def test_cfm13_action(self):
        self.assertEquals(self.cfm13_parsed_data[0]._action1, "Block")

    def test_cfm13_duration(self):
        self.assertEquals(self.cfm13_parsed_data[0]._duration1, "86400")
        self.assertIsNone(self.cfm13_parsed_data[0]._duration2)

    def test_cfm13_sensitivity(self):
        self.assertEquals(self.cfm13_parsed_data[0]._sensitivity, "noSensitivity")

    def test_cfm13_restriction(self):
        self.assertEquals(self.cfm13_parsed_data[0]._restriction, "AMBER")

    # CFM20 format tests
    def test_cfm20_content_returned(self):
        self.assertEquals(len(self.cfm20_parsed_data), 1)

    def test_cfm20_indicator(self):
        self.assertEquals(self.cfm20_parsed_data[0]._indicator, "8675:a289:5:102c::bd8:baac")

    def test_cfm20_indicator_type(self):
        self.assertEquals(self.cfm20_parsed_data[0]._indicatorType, "IPv6Address")

    def test_cfm20_action(self):
        self.assertEquals(self.cfm13_parsed_data[0]._action1, "Block")

    def test_cfm20_duration(self):
        self.assertEquals(self.cfm20_parsed_data[0]._duration1, "86400")
        self.assertIsNone(self.cfm20_parsed_data[0]._duration2)

    def test_cfm20_sensitivity(self):
        self.assertEquals(self.cfm20_parsed_data[0]._sensitivity, "noSensitivity")

    def test_cfm20_restriction(self):
        self.assertIsNone(self.cfm20_parsed_data[0]._restriction)

    # STIX format tests
    def test_stix_content_returned(self):
        self.assertEquals(len(self.stix_parsed_data), 11)

    def test_stix_indicator(self):
        self.assertEquals(self.stix_parsed_data[1]._indicator, "13.13.13.13")
        self.assertEquals(self.stix_parsed_data[9]._indicator, "bad.domain.be/poor/path")

    def test_stix_indicator_type(self):
        self.assertEquals(self.stix_parsed_data[1]._indicatorType, "IPv4Address")
        self.assertEquals(self.stix_parsed_data[5]._indicatorType, "FilePath")

    def test_stix_action(self):
        self.assertEquals(self.stix_parsed_data[1]._action1, "Block")

    def test_stix_duration(self):
        self.assertEquals(self.stix_parsed_data[1]._duration1, "86400")
        self.assertIsNone(self.stix_parsed_data[1]._duration2)

    def test_stix_sensitivity(self):
        self.assertEquals(self.stix_parsed_data[1]._sensitivity, "noSensitivity")

    def test_stix_restriction(self):
        self.assertIsNone(self.stix_parsed_data[1]._restriction)

if __name__ == '__main__':
    main()
