import bitmapist


class Tracker(object):
    def __init__(self, name='rapidsms-xray', host='localhost',
                 port=6379, db=3):
        bitmapist.setup_redis(name, host, port, db=db)

    def event(self, event_name, identifier, system='rapidsms-xray',
              now=None, track_hourly=None):
        bitmapist.mark_event(event_name, identifier,
                             system, now, track_hourly)
