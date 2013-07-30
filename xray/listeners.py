from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in
from django.contrib.auth.signals import user_logged_out

from .events import Tracker
from . import rolodex

tracker = Tracker()


@receiver(user_logged_in)
def receive_logged_in(**kwargs):
    request = kwargs.get("request")
    cleaver = request.environ['cleaver']

    tracker.web_event('logged_in', cleaver.identity)
    tracker.web_event('active', cleaver.identity)


@receiver(user_logged_out)
def receive_logged_out(**kwargs):
    request = kwargs.get("request")
    cleaver = request.environ['cleaver']

    tracker.web_event('logged_out', cleaver.identity)
    rolo = rolodex.Rolodex()
    rolo.expire_bid(request.environ['BID'])
