from __future__ import unicode_literals
import datetime

from django.conf import settings
from django.contrib.auth.models import User
import redis

from rapidsms.tests.harness import RapidTest

from .. import rolodex


class XrayTestBase(RapidTest):

    def setUp(self):
        self.prefix = "testxray"
        self.rolodex = rolodex.Rolodex(prefix=self.prefix)
        self.bitmapist_db = redis.Redis(host='localhost', port=6379, db=3)
        self.rolodex_db = redis.Redis(host='localhost', port=6379, db=4)
        self.cleaver_db = redis.Redis(host='localhost', port=6379, db=5)
        # Before doing anything else, we must clear out the dummy backend
        # as this is not automatically flushed between tests.
        self.clear_test_data()
        return super(XrayTestBase, self).setUp()

    def clear_test_data(self):
        # clear cleaver test data
        experiment_keys = self.cleaver_db.keys("%s:*" % self.prefix)
        for experiment_key in experiment_keys:
            self.experiment_db.delete(experiment_key)

        # clear rolodex test data
        rolodex_keys = self.rolodex_db.keys("%s:*" % self.prefix)
        for rolodex_key in rolodex_keys:
            self.rolodex_db.delete(rolodex_key)

        # clear bitmapist test data
        event_keys = self.bitmapist_db.keys("trackist_%s*" % self.prefix)
        for event_key in event_keys:
            self.bitmapist_db.delete(event_key)

        op_keys = self.bitmapist_db.keys("trackist_bitop_AND_trackist_%s*" %
                                         self.prefix)
        for op_key in op_keys:
            self.redis.bitmapist_db(op_key)

    def create_reporter(self, **kwargs):
        defaults = {
            'name': self.random_string(25),
            'birth_date': datetime.date(2010, 3, 14),
            'sex': 'M',
        }
        defaults.update(**kwargs)

        return defaults

    def create_user(self, username=None, password=None, email=None,
                    user_permissions=None, groups=None, **kwargs):
        username = username or self.random_string(25)
        password = password or self.random_string(25)
        email = email or '{0}@example.com'.format(self.random_string(25))
        user = User.objects.create_user(username, email, password)
        if user_permissions:
            user.user_permissions = user_permissions
        if groups:
            user.groups = groups
        if kwargs:
            User.objects.filter(pk=user.pk).update(**kwargs)
        return User.objects.get(pk=user.pk)
