
RapidSMS Xray
========================
RapidSMS app for web and SMS split test experiments & event tracking

Below you will find basic setup instructions for the rapidsms-xray
project. To begin you should have the following applications installed on your
local development system:

- Python >= 2.6 (2.7 recommended)
- `pip >= 1.1 <http://www.pip-installer.org/>`_
- `Redis >= 2.6.0 <http://redis.io>`_


Installation
------------

Please note: at the time of this writing, Ubuntu installs an older,
incompatible version of Redis (prior to the introduction of the `BITOP` and
`BITCOUNT` commands).
You can use the following PPA to install a more recent version::


    sudo add-apt-repository ppa:chris-lea/redis
    sudo apt-get update
    sudo apt-get install redis-server

Install necessary python requirements with pip::

    pip install -r requirements/base.txt

In your rapidsms project `settings.py`, add `xray` to your `INSTALLED_APPS` and
add `xray.context_processors.web_experiments` to your `TEMPLATE_CONTEXT_PROCESSORS`

In your rapidsms project `urls.py`, add xray's urls to `urlpatterns`::

    (r'^xray/', include('xray.urls')),

You may need to run django's `collectstatic` to ensure xray's static assests are
available::

    django-admin.py collectstatic


Experiments
-----------

rapidsms-xray uses `Cleaver <https://github.com/ryanpetrello/cleaver>`_
for split testing experiments. Please note that rapidsms-xray currently uses a
custom fork of Cleaver pending upstream merging of the RedisBackend (which will
be installed properly by `python setup.py install` or `pip install -r requirements/base.txt`).

To conduct web split testing experiments, add your experiments to
your app's ``context_processors.py`` which makes the experiment choice
available in the RequestContext. You don't have to put your experiments in a
context_processor -- its just a convenient location so they can all be in one place.

See `xray/context_processors.py 
<https://github.com/ewheeler/rapidsms-xray/blob/master/xray/context_processors.py>`_
and `thousand/templates/thousand/index.html
<https://github.com/ewheeler/rapidsms-thousand-days/blob/master/thousand/templates/thousand/index.html>`_ for example usage.

To conduct sms split testing experiments, add your experiments to your app.py or handler and
ensure that the ``experiments`` app is listed in your setting.py's ``INSTALLED_APPS``
`xray/app.py <https://github.com/ewheeler/rapidsms-xray/blob/master/xray/app.py>`_ will deal with identifying experiment participation during the router's
``filter`` phase, so experiments can be conducted in any of the subsequent incoming phases.

Please be aware that experiment participation is handled separately for web and sms
split testing (specifically, web participant identity is cookie-based for non-logged-in
uses and is user_id-based for logged-in users, whereas sms participant identity
is based on mobile number) -- that is, a web experiment participant cannot be scored
by a SMS conversion event and vice-versa.

See `xray/app.py
<https://github.com/ewheeler/rapidsms-xray/blob/master/xray/app.py>`_ for example usage.


Events
------

rapidsms-xray uses `bitmapist <https://github.com/Doist/bitmapist>`_
for event tracking and cohort analysis.

To use, import and instantiate `xray.events.Tracker` and then call
`my_tracker.web_event` or `my_tracker.sms_event` with an event name and the
user's cleaver identity. `xray.rolodex.Rolodex` caches identity information for
quick user lookup and issues a unique integer for each web and sms user. These
unique integer ids are used by bitmapist to track event participation using
Redis bitmaps for fast, arbitrary querying. See the bitmapist documentation for
additional information.
See `xray/app.py
<https://github.com/ewheeler/rapidsms-xray/blob/master/xray/app.py>`_
and `xray/views.py 
<https://github.com/ewheeler/rapidsms-xray/blob/master/xray/views.py>`_ for example usage.


When performing custom event analysis, use the *Events classes (with separate
Web* and SMS* classes for each time period) in `xray.events` rather than the
bitmapist classes -- rapidsms-xray adds prefixes to namespace the bitmapist
keys as well as prefixes to separate sms and web events.
`xray.events.Tracker`'s event methods add the appropriate prefixes, so you will
only need to worry about them if you are accessing bitmapist or the stored data
in Redis directly.


Dashboard
---------

rapidsms-xray includes a dashboard summarizing experiment and event
participation as well as drilldown pages showing experiment details and cohort
analysis of event participation.
