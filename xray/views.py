from __future__ import unicode_literals
from collections import defaultdict
import datetime
import json

from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.core.serializers.json import DjangoJSONEncoder

from cleaver.experiment import VariantStat
from cleaver.backend.redis import RedisBackend
from bitmapist import cohort

from .events import Tracker
from .events import WebWeekEvents
from .events import SMSWeekEvents

# TODO use project config?
backend = RedisBackend()
tracker = Tracker()


def index(request):
    cleaver = request.environ['cleaver']
    tracker.web_event('view_xray_dashboard', cleaver.identity)
    tracker.web_event('active', cleaver.identity)

    num_experiments = len(backend.all_experiments())
    now = datetime.datetime.utcnow()

    num_web_active_this_week = len(WebWeekEvents('active', now.year,
                                                 now.isocalendar()[1]))
    num_sms_active_this_week = len(SMSWeekEvents('active', now.year,
                                                 now.isocalendar()[1]))
    return render_to_response(
        "xray/index.html",
        {"experiments": num_experiments,
         "web_active": num_web_active_this_week,
         "sms_active": num_sms_active_this_week},
        context_instance=RequestContext(request))


def format_percentage(f):
    return '{:.2%}'.format(f) if f else None


def _experiment_data(experiment):
    control = VariantStat(experiment.control, experiment)
    data = {
        'name': experiment.name,
        'started_on': experiment.started_on,
        'participants': experiment.participants,
        'conversions': experiment.conversions,
        'control_conversion_rate': control.conversion_rate,
    }
    variants_data = {}
    for variant_name in experiment.variants:
        variant = VariantStat(variant_name, experiment)
        improvement_from_control = None
        if control.conversion_rate > 0:
            improvement_from_control =\
                format_percentage(abs((variant.conversion_rate /
                                       control.conversion_rate) - 1))
        variant_data = {
            'name': variant_name,
            'is_control': (variant_name == experiment.control),
            'participants': experiment.participants_for(variant),
            'conversions': experiment.conversions_for(variant),
            'conversion_rate': format_percentage(variant.conversion_rate),
            'z_score': variant.z_score,
            'confidence_level': variant.confidence_level,
            'improvement_from_control': improvement_from_control,
        }
        variants_data.update({variant_name: variant_data})
    data.update({'variants': variants_data})
    return data


def _experiments_data():
    experiments_data = {}
    for experiment in backend.all_experiments():
        experiments_data.update({experiment.name:
                                 _experiment_data(experiment)})
    return experiments_data


def experiments(request):
    cleaver = request.environ['cleaver']
    tracker.web_event('view_experiments', cleaver.identity)
    tracker.web_event('active', cleaver.identity)
    return render_to_response(
        "xray/experiments.html",
        {"experiments_data": _experiments_data()},
        context_instance=RequestContext(request))


def experiments_json(request):
    cleaver = request.environ['cleaver']
    tracker.web_event('view_experiments_json', cleaver.identity)
    return HttpResponse(json.dumps(_experiments_data(), cls=DjangoJSONEncoder),
                        mimetype="application/json")


def _events_dates(events):
    dates = {'days': False, 'weeks': False, 'months': False}
    for event in events:
        if 'W' in event.date:
            dates['weeks'] = True
        elif len(event.date.split('-')) == 3:
            dates['days'] = True
        elif len(event.date.split('-')) == 2:
            dates['months'] = True
        else:
            raise RuntimeError('Unknown event date')
    return [k for k, v in dates.items() if v]


def events(request):
    events = tracker.get_events()

    web_events = [e for e in events if e.kind == 'web']
    sms_events = [e for e in events if e.kind == 'sms']

    web_dates = _events_dates(web_events)
    sms_dates = _events_dates(sms_events)

    return render_to_response(
        "xray/events_form.html",
        {"web_events": set([(e.name, e.display) for e in web_events]),
         "web_dates": web_dates,
         "sms_events": set([(e.name, e.display) for e in sms_events]),
         "sms_dates": sms_dates},
        context_instance=RequestContext(request))


def events_data(request):
    event_kind = request.GET.get('event_kind')
    assert event_kind in ['web', 'sms']
    time_group = request.GET.get('%s_time_group' % event_kind)
    data = cohort.get_dates_data(select1=request.GET.get('%s_select1' %
                                                         event_kind),
                                 select2=request.GET.get('%s_select2' %
                                                         event_kind),
                                 time_group=time_group,
                                 system='rapidsms-xray')

    averages = defaultdict(int)

    for column in xrange(2, 15):
        for row in data:
            if row[column]:
                averages['%d-count' % column] += 1
                averages['%d-total' % column] += row[column]

    return render_to_response(
        "xray/events_data.html",
        {"dates_data": data,
         "time_group": time_group,
         "averages": averages},
        context_instance=RequestContext(request))
