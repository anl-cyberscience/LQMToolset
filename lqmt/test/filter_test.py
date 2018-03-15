import toml
import json
import arrow
from unittest import TestCase, main
from lqmt.test.test_data.filters.filter_configs import TESTCONFIG1
from lqmt.test.test_data.filters.filter_inputs import INPUT1
from lqmt.lqm.filters import SourceFilters


class TestFilters(TestCase):
    def setUp(self):
        self.user_config = toml.loads(TESTCONFIG1)
        self.filters = SourceFilters(self.user_config['Filter']['Source'][0])

    def test_all_filters(self):
        meta = json.loads(INPUT1)
        # true case
        meta['SentTimestamp'] = str(arrow.utcnow().timestamp)
        self.assertTrue(self.filters.checkAllFilters(meta))
        # fail sending site
        meta['SendingSite'] = 'TEST3'
        self.assertFalse(self.filters.checkAllFilters(meta))
        # fail payload type
        meta = json.loads(INPUT1)
        meta['PayloadType'] = 'Report'
        self.assertFalse(self.filters.checkAllFilters(meta))
        # fail payload format
        meta = json.loads(INPUT1)
        meta['PayloadFormat'] = 'OtherPDF'
        self.assertFalse(self.filters.checkAllFilters(meta))
        # fail sensitivity
        meta = json.loads(INPUT1)
        meta['DataSensitivity'] = 'OUO'
        self.assertFalse(self.filters.checkAllFilters(meta))
        # fail restrictions
        meta = json.loads(INPUT1)
        meta['SharingRestrictions'] = 'AMBER'
        self.assertFalse(self.filters.checkAllFilters(meta))
        # fail recon policy
        meta = json.loads(INPUT1)
        meta['ReconPolicy'] = 'Touch'
        self.assertFalse(self.filters.checkAllFilters(meta))
        # fail file age
        meta = json.loads(INPUT1)
        meta['SentTimestamp'] = str(arrow.utcnow().shift(months=-2, seconds=-10).timestamp)
        self.assertFalse(self.filters.checkAllFilters(meta))

    def test_site_includes(self):
        meta = json.loads(INPUT1)
        # test site includes
        self.assertTrue(self.filters.checkSendingSite(meta))
        # test lower case
        meta['SendingSite'] = 'TEST3'
        self.assertFalse(self.filters.checkSendingSite(meta))
        # test empty
        self.filters._site_includes = []
        self.assertTrue(self.filters.checkSendingSite(meta))

    def test_site_excludes(self):
        meta = json.loads(INPUT1)
        self.filters._site_includes = []
        # check includes empty and site not in excludes
        self.assertTrue(self.filters.checkSendingSite(meta))
        # check site in the excludes list
        meta['SendingSite'] = 'SITE2'
        self.assertFalse(self.filters.checkSendingSite(meta))
        # check empty excludes list
        self.filters._site_excludes = []
        self.assertTrue(self.filters.checkSendingSite(meta))

    def test_payload_types(self):
        meta = json.loads(INPUT1)
        # test type in the list
        self.assertTrue(self.filters.checkPayloadType(meta))
        # test unexpected list
        meta['PayloadType'] = 'Report'
        self.assertFalse(self.filters.checkPayloadType(meta))
        # test empty list
        self.filters._payload_types = []
        self.assertTrue(self.filters.checkPayloadType(meta))

    def test_payload_formats(self):
        meta = json.loads(INPUT1)
        # test format in the list
        self.assertTrue(self.filters.checkPayloadFormat(meta))
        # test unexpected list
        meta['PayloadFormat'] = 'OtherPDF'
        self.assertFalse(self.filters.checkPayloadFormat(meta))
        # test empty list
        self.filters._payload_formats = []
        self.assertTrue(self.filters.checkPayloadFormat(meta))

    def test_sensitivities(self):
        meta = json.loads(INPUT1)
        # test format in the list
        self.assertTrue(self.filters.checkDataSensitivity(meta))
        # test unexpected list
        meta['DataSensitivity'] = 'OUO'
        self.assertFalse(self.filters.checkDataSensitivity(meta))
        # test empty list
        self.filters._sensitivities = []
        self.assertTrue(self.filters.checkDataSensitivity(meta))

    def test_restrictions(self):
        meta = json.loads(INPUT1)
        # test format in the list
        self.assertTrue(self.filters.checkSharingRestrictions(meta))
        # test unexpected list
        meta['SharingRestrictions'] = 'AMBER'
        self.assertFalse(self.filters.checkSharingRestrictions(meta))
        # test empty list
        self.filters._restrictions = []
        self.assertTrue(self.filters.checkSharingRestrictions(meta))

    def test_reconn(self):
        meta = json.loads(INPUT1)
        # test format in the list
        self.assertTrue(self.filters.checkReconPolicy(meta))
        # test unexpected list
        meta['ReconPolicy'] = 'Touch'
        self.assertFalse(self.filters.checkReconPolicy(meta))
        # test empty list
        self.filters._reconnaissance = []
        self.assertTrue(self.filters.checkReconPolicy(meta))

    def test_no_file_age(self):
        meta = json.loads(INPUT1)
        # check no setting
        self.filters._max_file_age = None
        self.assertTrue(self.filters.checkFileAge(meta))

    def test_file_age(self):
        # utilizes tests for month
        meta = json.loads(INPUT1)
        now = arrow.utcnow()
        meta['SentTimestamp'] = str(now.timestamp)
        # check true
        self.assertTrue(self.filters.checkFileAge(meta))
        # check false
        meta['SentTimestamp'] = str(now.shift(months=-2, seconds=-10).timestamp)
        self.assertFalse(self.filters.checkFileAge(meta))

    def test_file_age_sec(self):
        meta = json.loads(INPUT1)
        now = arrow.utcnow()
        self.filters._max_file_age = "30 secs"
        meta['SentTimestamp'] = str(now.timestamp)
        # check true
        self.assertTrue(self.filters.checkFileAge(meta))
        # check false
        meta['SentTimestamp'] = str(now.shift(seconds=-35).timestamp)
        self.assertFalse(self.filters.checkFileAge(meta))

    def test_file_age_min(self):
        meta = json.loads(INPUT1)
        now = arrow.utcnow()
        self.filters._max_file_age = "30 min"
        meta['SentTimestamp'] = str(now.timestamp)
        # check true
        self.assertTrue(self.filters.checkFileAge(meta))
        # check false
        meta['SentTimestamp'] = str(now.shift(minutes=-30, seconds=-10).timestamp)
        self.assertFalse(self.filters.checkFileAge(meta))

    def test_file_age_hour(self):
        meta = json.loads(INPUT1)
        now = arrow.utcnow()
        self.filters._max_file_age = "1 hour"
        meta['SentTimestamp'] = str(now.timestamp)
        # check true
        self.assertTrue(self.filters.checkFileAge(meta))
        # check false
        meta['SentTimestamp'] = str(now.shift(hours=-1, seconds=-10).timestamp)
        self.assertFalse(self.filters.checkFileAge(meta))

    def test_file_age_day(self):
        meta = json.loads(INPUT1)
        now = arrow.utcnow()
        self.filters._max_file_age = "2 days"
        meta['SentTimestamp'] = str(now.timestamp)
        # check true
        self.assertTrue(self.filters.checkFileAge(meta))
        # check false
        meta['SentTimestamp'] = str(now.shift(days=-2, seconds=-10).timestamp)
        self.assertFalse(self.filters.checkFileAge(meta))

    def test_file_age_week(self):
        meta = json.loads(INPUT1)
        now = arrow.utcnow()
        self.filters._max_file_age = "1 week"
        meta['SentTimestamp'] = str(now.timestamp)
        # check true
        self.assertTrue(self.filters.checkFileAge(meta))
        # check false
        meta['SentTimestamp'] = str(now.shift(weeks=-1, seconds=-10).timestamp)
        self.assertFalse(self.filters.checkFileAge(meta))

    def test_file_age_yr(self):
        meta = json.loads(INPUT1)
        now = arrow.utcnow()
        self.filters._max_file_age = "3 yrs"
        meta['SentTimestamp'] = str(now.timestamp)
        # check true
        self.assertTrue(self.filters.checkFileAge(meta))
        # check false
        meta['SentTimestamp'] = str(now.shift(years=-3, seconds=-10).timestamp)
        self.assertFalse(self.filters.checkFileAge(meta))


if __name__ == '__main__':
    main()
