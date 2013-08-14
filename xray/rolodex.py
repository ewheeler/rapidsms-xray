import hashlib

import redis
import phonenumbers

from django.conf import settings

# thanks to:
# http://mobiforge.com/forum/running/analytics/
# stats-and-unique-vistors-different-mobile
# and
# http://mobiforge.com/developing/blog/useful-x-headers
headers_for_fingerprint = ['USER-AGENT', 'HOST', 'ACCEPT', 'ACCEPT-LANGUAGE',
                           'ACCEPT-CHARSET', 'X-REAL-IP', 'X-FORWARDED-HOST',
                           'HTTP-X-REAL-IP', 'HTTP_X_FORWARDED_FOR',
                           'HTTP_USER_AGENT', 'HTTP_DNT', 'HTTP_ACCEPT',
                           'HTTP_ACCEPT_LANGUAGE', 'HTTP_ACCEPT_ENCODING',
                           'X-FORWARDED-SERVER', 'X-FORWARDED-FOR',
                           'X-UP-SUBNO', 'X-NOKIA-MSISDN',
                           'X-UP-CALLING-LINE-ID', 'X-HTS-CLID',
                           'X-H3G-MSISDN', 'X-NX-CLID', 'X-ACCESS-SUBNYM',
                           'X-ORANGE-ID', 'MSISDN', 'X-WAP-PROFILE',
                           'X-WAP-PROFILE-DIFF', 'X-APN-ID',
                           'X-DRUTT-DEVICE-ID', 'X-DRUTT-PORTAL-USER-ID',
                           'X-DRUTT-PORTAL-USER-MSISDN', 'X-GGSNIP',
                           'X-JPHONE-COLOR', 'X-JPHONE-DISPLAY',
                           'X-NETWORK-INFO', 'X-OS-PREFS', 'X-NOKIA-ALIAS',
                           'X-NOKIA-BEARER', 'X-NOKIA-IMSI', 'X-NOKIA-MSISDN',
                           'X-OPERAMINI-PHONE', 'X-ORIGINAL-USER-AGENT',
                           'X-IMSI', 'X-MSISDN']


class Hashabledict(dict):
    # from http://stackoverflow.com/a/16162138
    def __hash__(self):
        return hash((frozenset(self), frozenset(self.itervalues())))


class Rolodex(object):
    # 'mobile id'
    # mid = hashlib.md5(e164-formatted-msisdn).hexdigest()

    # find uid from phone number
    # (string) 'uid:{{ e164 }}' => uid
    # find uid from mid
    # (string) 'uid:{{ mid }}' => uid
    # find uid from bid
    # (string) 'uid:{{ bid }}' => uid

    # find phone number from mid
    # (string) 'e164:{{ mid }}' => e164

    # find count of phone activity
    # (sortedset) midCounts => (mid,n) where n is number of lookups

    # find count of browser activity
    # (sortedset) bidCounts => (bid,n) where n is number of lookups

    # find browsers used by mid
    # (set) 'bid:{{ mid }}' => (bid,...)

    # find uid and mid from browser
    # (hash) 'bid:{{ bid }}' => {'uid': uid, 'mid': mid}

    # seen mids
    # (set) midSeen => (mid,...)
    # registered mids
    # (set) midRegistered => (mid,...)

    # find mids used by uid
    # (set) 'mids:{{ uid }}' => (mid,...)

    # find browsers used by uid
    # (set) 'bids:{{ uid }}' => (bid,...)

    # invalid msisdn for country, scored by frequency
    # (sorted set) 'invalid:msisdn:{{ country }}' => ((1234, 22),(5678, 8),...)

    def __init__(self, host='localhost', port=6379, db=4, prefix="rolodex",
                 country='UG'):
        assert country in phonenumbers.SUPPORTED_REGIONS
        self.prefix = prefix
        # TODO allow list of countries?
        self.country = country
        self.redis = redis.Redis(host=host, port=port, db=db)
        self.SessionStore = __import__(settings.SESSION_ENGINE,
                                       fromlist=['']).SessionStore


    def xid(self, hashable):

        # unique ids must be smaller than 2**32 -1 in order
        # to use redis' bitmaps to store event data.
        # and the smaller, the better, as it will use less RAM.
        # so, for each unique md5 hash, issue an integer

        hashed = hashlib.md5(hashable).hexdigest()

        existing = self.redis.get('%s:xid:%s' % (self.prefix, hashed))
        if existing:
            return existing

        # increment counter
        integer_id = self.redis.incrby('%s:xray_identity_counter' %
                                       self.prefix, 1)
        # set maps
        self.redis.set('%s:xid:%s' % (self.prefix, hashed), integer_id)
        self.redis.set('%s:xid:%s' % (self.prefix, integer_id), hashed)
        return integer_id

    def format_msisdn(self, msisdn=None):
        """ given a msisdn, return in E164 format """
        assert msisdn is not None
        num = phonenumbers.parse(msisdn, self.country)
        is_valid = phonenumbers.is_valid_number(num)
        if not is_valid:
            #raise RuntimeError("%s is not a valid number for %s"
            #                   % (msisdn, self.country))
            # create or increment count of  invalid number
            self.redis.zadd('%s:invalid:msisdn:%s' %
                            (self.prefix, self.country), msisdn, 1.0)
            return msisdn
        return phonenumbers.format_number(num,
                                          phonenumbers.PhoneNumberFormat.E164)

    def mid_for_msisdn(self, msisdn=None):
        assert msisdn is not None
        return self.xid(self.format_msisdn(msisdn))

    def _seen_mid_registered(self, mid):
        self.redis.sadd('%s:midRegistered' % self.prefix, mid)

    def _seen_mid(self, mid, e164):
        self.redis.zincrby('%s:midCounts' % self.prefix, mid, 1.0)
        self.redis.set('%s:e164:%s' % (self.prefix, mid), e164)
        self.redis.sadd('%s:midSeen' % self.prefix, mid)

    def uid_for_mid(self, mid):
        return self.redis.get('%s:uid:%s' % (self.prefix, mid))

    def mids_for_uid(self, uid):
        return self.redis.smembers('%s:mids:%s' % (self.prefix, uid))

    def _seen_bid(self, bid, uid, sid):
        self.redis.zincrby('%s:bidCounts' % self.prefix, bid)
        if uid is not None:
            self.redis.hmset('%s:ids:%s' % (self.prefix, bid),
                             {'uid': uid, 'sid': sid})
            # cache only for 2 minutes. if browser activity continues, value
            # will be recached
            self.redis.expire('%s:ids:%s' % (self.prefix, bid), 120)
            return True
        return None

    def ids_for_bid(self, bid):
        if self.redis.hexists('%s:ids:%s' % (self.prefix, bid), 'uid'):
            return self.redis.hgetall('%s:ids:%s' % (self.prefix, bid))
        return None

    def expire_bid(self, bid):
        if self.redis.exists('%s:ids:%s' % (self.prefix, bid)):
            return self.redis.delete('%s:ids:%s' % (self.prefix, bid))
        return None

    def lookup_msisdn(self, msisdn=None):
        assert msisdn is not None
        e164 = self.format_msisdn(msisdn)
        mid = None
        uid = None
        if e164:
            mid = self.xid(e164)
        else:
            # if number cannot be e164 formatted,
            # return hash of string
            # could be an operator's message, etc
            mid = self.xid(msisdn)

        self._seen_mid(mid, e164)

        uid = self.uid_for_mid(mid)
        if uid:
            self._seen_mid_registered(mid)

        return {'mid': mid, 'uid': uid}

    def fingerprint_environ(self, hashable_environ):
        headers_up = dict(((k.upper(), v) for k, v
                           in hashable_environ.iteritems()
                           if isinstance(v, str)))
        header_info = []
        for header in headers_for_fingerprint:
            header_info.append(headers_up.get(header, ''))
        xid = self.xid(''.join(header_info).replace(' ', ''))
        return int(xid)

    def lookup_browser(self, environ):
        bid = None
        uid = None
        sid = None
        hashable_environ = Hashabledict(environ)
        bid = self.fingerprint_environ(hashable_environ)

        if self.ids_for_bid(bid):
            self._seen_bid(bid, uid, sid)
            # add 'bid': bid to cached values and return
            return dict([('bid', bid)] + self.ids_for_bid(bid).items())

        if 'HTTP_COOKIE' in environ:
            cookie = {s.split('=')[0].strip(): s.split('=')[1].strip()
                      for s in environ['HTTP_COOKIE'].split(';')}
            if 'sessionid' in cookie:
                sid = self.xid(cookie['sessionid'])
                environ['SID'] = sid
                session = self.SessionStore(session_key=cookie['sessionid'])
                if session.exists(cookie['sessionid']):
                    session.load()
                    uid = self.xid(str(session.get('_auth_user_id')))
        self._seen_bid(bid, uid, sid)
        return {'uid': uid, 'bid': bid, 'sid': sid}
