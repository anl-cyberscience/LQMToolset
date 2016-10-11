import os
from unittest import TestCase, main
import lqmt.whitelist.master as master


class TestWhitelist(TestCase):
    """
    Testing class for whitelist function. Used to test if a value belongs in the user defined whitelist or not.
    """

    def setUp(self):
        currentdir = os.path.dirname(__file__)
        whitelist = currentdir + "/test_data/whitelist/whitelist.txt"
        db = currentdir + "/test_data/whitelist/whitelist.db"
        configstr = """
        [Whitelist]
            whitelist = '{0}'
            dbfile = '{1}'
        """.format(whitelist, db)

        self.wl = master.MasterWhitelist(configStr=configstr)
        self.indicatorTypes = master.IndicatorTypes

    # IPV4 Addresses
    def test_match_by_ipv4(self):
        self.assertTrue(self.wl.isWhitelisted(self.indicatorTypes.ipv4, '192.168.1.1'))

    def test_failed_match_by_ipv4(self):
        self.assertFalse(self.wl.isWhitelisted(self.indicatorTypes.ipv4, '192.168.1.2'))

    def test_match_ipv4_by_subnet(self):
        self.assertTrue(self.wl.isWhitelisted(self.indicatorTypes.ipv4, '192.168.2.5'))

    # IPV4 Subnets
    def test_match_ipv4_sub_by_inclusion(self):
        self.assertTrue(self.wl.isWhitelisted(self.indicatorTypes.ipv4subnet, '192.168.2.0/26'))

    def test_match_contiguous_ipv4_sub(self):
        self.assertTrue(self.wl.isWhitelisted(self.indicatorTypes.ipv4subnet, '192.168.2.0/23'))

    def test_failed_match_large_ipv4_sub(self):
        self.assertFalse(self.wl.isWhitelisted(self.indicatorTypes.ipv4subnet, '192.168.2.0/22'))

    def test_failed_match_ipv4_sub(self):
        self.assertFalse(self.wl.isWhitelisted(self.indicatorTypes.ipv4subnet, '192.168.20/24'))

    # IPV6 Addresses
    def test_match_by_ipv6(self):
        self.assertTrue(self.wl.isWhitelisted(self.indicatorTypes.ipv6, '6EE2:317F:0AF1:684C:AAC8:43F4:6E49:7D86'))

    def test_failed_match_by_ipv6(self):
        self.assertFalse(self.wl.isWhitelisted(self.indicatorTypes.ipv6, '6EE2:317F:0AF1:684C:AAC8:43F4:6E49:AAAA'))

    # Domains
    def test_match_domain(self):
        self.assertTrue(self.wl.isWhitelisted(self.indicatorTypes.domain, 'thegoodguys.com'))

    def test_failed_match_domain(self):
        self.assertFalse(self.wl.isWhitelisted(self.indicatorTypes.domain, 'badguy.com'))

    # Host
    def test_match_host_by_domain(self):
        self.assertTrue(self.wl.isWhitelisted(self.indicatorTypes.host, 'oneof.thegoodguys.com'))

    def test_match_host(self):
        self.assertTrue(self.wl.isWhitelisted(self.indicatorTypes.host, 'really.goodguy.com'))

    def test_failed_match_host_by_url(self):
        self.assertFalse(self.wl.isWhitelisted(self.indicatorTypes.url, 'very.badguy.com'))

    # URL
    def test_match_by_url(self):
        self.assertTrue(
            self.wl.isWhitelisted(self.indicatorTypes.url, 'http://www.goodsite.com/blah?someparm=9&parm2=foo#anchor'))

    def test_failed_match_by_url(self):
        self.assertFalse(
            self.wl.isWhitelisted(self.indicatorTypes.url, 'http://www.badsite.com/blah?someparm=9&parm2=foo#anchor'))


if __name__ == '__main__':
    main()
