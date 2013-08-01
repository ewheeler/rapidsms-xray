from collections import namedtuple
import bitmapist

Event = namedtuple('Event', 'prefix, kind, name, date, display')


class Tracker(object):
    def __init__(self, name='rapidsms-xray', prefix='xray', host='localhost',
                 port=6379, db=3):
        self.prefix = prefix
        bitmapist.setup_redis(name, host, port, db=db)

    def _event(self, event_name, identifier, system='rapidsms-xray',
               now=None, track_hourly=None):
        bitmapist.mark_event(event_name=event_name, uuid=identifier,
                             system=system, now=now, track_hourly=track_hourly)

    def web_event(self, event_name, identifier, system='rapidsms-xray',
                  now=None, track_hourly=None):
        event_name = '%s:web:%s' % (self.prefix, event_name)
        #print ('EVENT %s %s' % (event_name, identifier))
        self._event(event_name, identifier, system, now, track_hourly)

    def sms_event(self, event_name, identifier, system='rapidsms-xray',
                  now=None, track_hourly=None):
        event_name = '%s:sms:%s' % (self.prefix, event_name)
        #print ('EVENT %s %s' % (event_name, identifier))
        self._event(event_name, identifier, system, now, track_hourly)

    def get_events(self):
        redis = bitmapist.get_redis('rapidsms-xray')
        all_keys = redis.keys('trackist_%s:*' % self.prefix)
        events = []
        for key in all_keys:
            prefix, kind, event_info = key.split(':')
            event_info_list = event_info.split('_')
            event_date = event_info_list.pop()
            event_display = ' '.join(event_info_list)
            event_name = '_'.join(event_info_list)
            events.append(Event._make((prefix, kind, event_name, event_date,
                                       event_display)))
        return events


# TODO pypi has old version without  bitmapist.MixinEventsMisc (which replaces
# MixinEventsMarked)
class WebWeekEvents(bitmapist.MixinCounts, bitmapist.MixinContains,
                    bitmapist.MixinEventsMarked):
    def __init__(self, event_name, year, week, system='rapidsms-xray',
                 prefix='xray'):
        self.system = system
        self.prefix = prefix
        event_name = '%s:web:%s' % (self.prefix, event_name)
        self.redis_key = bitmapist._prefix_key(event_name,
                                               'W%s-%s' % (year, week))


class SMSWeekEvents(bitmapist.MixinCounts, bitmapist.MixinContains,
                    bitmapist.MixinEventsMarked):
    def __init__(self, event_name, year, week, system='rapidsms-xray',
                 prefix='xray'):
        self.system = system
        self.prefix = prefix
        event_name = '%s:sms:%s' % (self.prefix, event_name)
        self.redis_key = bitmapist._prefix_key(event_name,
                                               'W%s-%s' % (year, week))


class WebMonthEvents(bitmapist.MixinCounts, bitmapist.MixinContains,
                     bitmapist.MixinEventsMarked):
    def __init__(self, event_name, year, month, system='rapidsms-xray',
                 prefix='xray'):
        self.system = system
        self.prefix = prefix
        event_name = '%s:web:%s' % (self.prefix, event_name)
        self.redis_key = bitmapist._prefix_key(event_name,
                                               '%s-%s' % (year, month))


class SMSMonthEvents(bitmapist.MixinCounts, bitmapist.MixinContains,
                     bitmapist.MixinEventsMarked):
    def __init__(self, event_name, year, month, system='rapidsms-xray',
                 prefix='xray'):
        self.system = system
        self.prefix = prefix
        event_name = '%s:sms:%s' % (self.prefix, event_name)
        self.redis_key = bitmapist._prefix_key(event_name,
                                               '%s-%s' % (year, month))


class WebDayEvents(bitmapist.MixinCounts, bitmapist.MixinContains,
                   bitmapist.MixinEventsMarked):
    def __init__(self, event_name, year, month, day, system='rapidsms-xray',
                 prefix='xray'):
        self.system = system
        self.prefix = prefix
        event_name = '%s:web:%s' % (self.prefix, event_name)
        self.redis_key = bitmapist._prefix_key(event_name,
                                               '%s-%s-%s' % (year, month, day))


class SMSDayEvents(bitmapist.MixinCounts, bitmapist.MixinContains,
                   bitmapist.MixinEventsMarked):
    def __init__(self, event_name, year, month, day, system='rapidsms-xray',
                 prefix='xray'):
        self.system = system
        self.prefix = prefix
        event_name = '%s:sms:%s' % (self.prefix, event_name)
        self.redis_key = bitmapist._prefix_key(event_name,
                                               '%s-%s-%s' % (year, month, day))


class WebHourEvents(bitmapist.MixinCounts, bitmapist.MixinContains,
                    bitmapist.MixinEventsMarked):
    def __init__(self, event_name, year, month, day, hour,
                 system='rapidsms-xray', prefix='xray'):
        self.system = system
        self.prefix = prefix
        event_name = '%s:web:%s' % (self.prefix, event_name)
        self.redis_key = bitmapist._prefix_key(event_name,
                                               '%s-%s-%s-%s' %
                                               (year, month, day, hour))


class SMSHourEvents(bitmapist.MixinCounts, bitmapist.MixinContains,
                    bitmapist.MixinEventsMarked):
    def __init__(self, event_name, year, month, day, hour,
                 system='rapidsms-xray', prefix='xray'):
        self.system = system
        self.prefix = prefix
        event_name = '%s:sms:%s' % (self.prefix, event_name)
        self.redis_key = bitmapist._prefix_key(event_name,
                                               '%s-%s-%s-%s' %
                                               (year, month, day, hour))
