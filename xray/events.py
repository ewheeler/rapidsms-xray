from collections import namedtuple
import bitmapist

Event = namedtuple('Event', 'prefix, kind, name, date, display')


class Tracker(object):
    def __init__(self, name='rapidsms-xray', host='localhost',
                 port=6379, db=3):
        bitmapist.setup_redis(name, host, port, db=db)

    def _event(self, event_name, identifier, system='rapidsms-xray',
               now=None, track_hourly=None):
        bitmapist.mark_event(event_name, identifier,
                             system, now, track_hourly)

    def web_event(self, event_name, identifier, system='rapidsms-xray',
                  now=None, track_hourly=None):
        event_name = 'xray:web:%s' % event_name
        self._event(event_name, identifier, system, now, track_hourly)

    def sms_event(self, event_name, identifier, system='rapidsms-xray',
                  now=None, track_hourly=None):
        event_name = 'xray:sms:%s' % event_name
        self._event(event_name, identifier, system, now, track_hourly)

    def get_events(self):
        redis = bitmapist.get_redis('rapidsms-xray')
        all_keys = redis.keys('trackist_*')
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
