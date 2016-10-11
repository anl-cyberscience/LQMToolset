from unittest import TestCase, main
from lqmt.lqm.parsers.FlexTransform.parser import FlexTransformParser
from lqmt.lqm.systemconfig import SystemConfig
from lqmt.test.test_data.sample_inputs import CFM13ALERT, CFM20ALERT
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
        self.flext.addParser('LQMTools', 'resources/sampleConfigurations/lqmtools.cfg')
        self.flext.addParser('Cfm13Alert', 'resources/sampleConfigurations/cfm13.cfg')
        self.flext.addParser('Cfm20Alert', 'resources/sampleConfigurations/cfm20alert.cfg')
        self.flext.addParser('stixtlp', 'resources/sampleConfigurations/stix_tlp.cfg')

        # Standard timestamp that can be used so all meta files use the same time and for easier validation
        self.time = str(time.time()).split('.')[0]

        # Parse all the data ahead of the tests
        self.cfm13_parsed_data = self.flext.parse(io.StringIO(CFM13ALERT), self.getMeta("Cfm13Alert"))
        self.cfm20_parsed_data = self.flext.parse(io.StringIO(CFM20ALERT), self.getMeta("Cfm20Alert"))

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

    def test_cfm13_detectedTime(self):
        pass
        # self.assertEquals(self.cfm13_parsed_data[0]._detectedTime, 1456116353.0)

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

    def test_cfm20_detectedTime(self):
        pass

    def test_cfm20_duration(self):
        self.assertEquals(self.cfm20_parsed_data[0]._duration1, "86400")
        self.assertIsNone(self.cfm20_parsed_data[0]._duration2)

    def test_cfm20_sensitivity(self):
        self.assertEquals(self.cfm20_parsed_data[0]._sensitivity, "noSensitivity")

    def test_cfm20_restriction(self):
        self.assertIsNone(self.cfm20_parsed_data[0]._restriction)

    # STIX TLP format tests
    def test_stix_tlp(self):
        pass

if __name__ == '__main__':
    main()
