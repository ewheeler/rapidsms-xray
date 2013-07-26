from __future__ import unicode_literals
import json

from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.core.serializers.json import DjangoJSONEncoder

from cleaver.experiment import VariantStat
from cleaver.backend.redis import RedisBackend

# TODO use project config?
backend = RedisBackend()


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
                                       control.conversion_rate) - 1)),
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
    return render_to_response(
        "xray/experiments.html",
        {"experiments_data": _experiments_data()},
        context_instance=RequestContext(request))


def experiments_json(request):
    return HttpResponse(json.dumps(_experiments_data(), cls=DjangoJSONEncoder),
                        mimetype="application/json")
