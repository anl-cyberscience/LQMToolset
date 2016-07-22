import os
from unittest import TestCase, main
import lqmt.whitelist.master as master


class TestWhitelist(TestCase):
    def setUp(self):
        currentdir = os.path.dirname(__file__)
        whitelist = currentdir + "\\test-data\\whitelist\\whitelist.txt"
        db = currentdir + "\\test-data\\whitelist\\whitelist.db"
        configstr = """
        [Whitelist]
            whitelist = '{0}'
            dbfile = '{1}'
        """.format(whitelist, db)

        self.wl = master.MasterWhitelist(configStr=configstr)
        self.indicatorTypes = master.IndicatorTypes

    def test_match_by_ip(self):
        self.assertTrue(self.wl.isWhitelisted(self.indicatorTypes.ipv4, '192.168.1.1'))

    def test_failed_match_by_ip(self):
        self.assertFalse(self.wl.isWhitelisted(self.indicatorTypes.ipv4, '192.168.1.2'))

    def test_match_by_subnet(self):
        self.assertTrue(self.wl.isWhitelisted(self.indicatorTypes.ipv4, '192.168.2.5'))


if __name__ == '__main__':
    main()
