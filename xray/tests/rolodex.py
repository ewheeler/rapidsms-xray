from __future__ import unicode_literals
from wsgiref.util import setup_testing_defaults

from .base import XrayTestBase
from .headers import headers
import sys


def debug(msg):
    sys.stdout.write(' %s ' % str(msg))
    sys.stdout.flush()


class RolodexTest(XrayTestBase):

    def setUp(self):
        super(RolodexTest, self).setUp()


class RolodexWebIDTest(RolodexTest):

    def test_lookup_browser(self):
        # lookup_browser returns same fingerprint
        environ_one = headers[0]
        setup_testing_defaults(environ_one)

        browser_one_ids = self.rolodex.lookup_browser(environ_one)
        assert browser_one_ids['bid'] == 1

        browser_count = self.rolodex_db.zrange('%s:bidCounts' % self.prefix,
                                               0, 1000)
        assert len(browser_count) == 1
        browser_one_seen = self.rolodex_db.zscore('%s:bidCounts' % self.prefix,
                                                  browser_one_ids['bid'])
        assert browser_one_seen == 1

        # lookup_browser issues only one xid for same headers
        browser_one_ids2 = self.rolodex.lookup_browser(environ_one)
        assert browser_one_ids['bid'] == browser_one_ids2['bid']

        browser_count = self.rolodex_db.zrange('%s:bidCounts' % self.prefix,
                                               0, 1000)
        assert len(browser_count) == 1

        browser_one_seen = self.rolodex_db.zscore('%s:bidCounts' % self.prefix,
                                                  browser_one_ids['bid'])
        assert browser_one_seen == 2

        # bidcounts is incremented
        environ_two = headers[1]
        setup_testing_defaults(environ_two)
        browser_two_ids = self.rolodex.lookup_browser(environ_two)

        assert browser_two_ids['bid'] != browser_one_ids['bid']
        assert browser_two_ids['bid'] == 2
        browser_count = self.rolodex_db.zrange('%s:bidCounts' % self.prefix,
                                               0, 1000)
        assert len(browser_count) == 2

        browser_one_seen = self.rolodex_db.zscore('%s:bidCounts' % self.prefix,
                                                  browser_one_ids['bid'])
        assert browser_one_seen == 2
        browser_two_seen = self.rolodex_db.zscore('%s:bidCounts' % self.prefix,
                                                  browser_two_ids['bid'])
        assert browser_two_seen == 1
        # TODO :ids: is set
        # TODO :ids: expires

        # TODO same browser logs in, issued different xid
        # TODO log in with another browers, gets same xid
        pass


class RolodexSMSIDTest(RolodexTest):
    # TODO lookup_msisdn returns same fingerprint
    # TODO lookup_msisdn issues only one xid
    # TODO mappings are created
    pass
