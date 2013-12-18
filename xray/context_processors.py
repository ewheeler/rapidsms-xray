
def web_experiments(request):
    cleaver = request.environ.get('cleaver')
    experiments = {}

    if cleaver is None:
        return experiments

    experiments['web_xray_dashboard_experiments_icon_variant'] = cleaver(
        'web_xray_dashboard_experiments_icon',
        ('beaker', 'icon-beaker'),
        ('stethoscope', 'icon-stethoscope')
    )

    experiments['web_xray_dashboard_phone_icon_variant'] = cleaver(
        'web_xray_dashboard_phone_icon',
        ('mobile-phone', 'icon-mobile-phone'),
        ('phone', 'icon-phone'),
        ('phone-sign', 'icon-phone-sign')
    )

    experiments['web_xray_dashboard_web_icon_variant'] = cleaver(
        'web_xray_dashboard_web_icon',
        ('laptop', 'icon-laptop'),
        ('desktop', 'icon-desktop')
    )

    if request.path == '/xray/events/':
        cleaver.score('web_xray_dashboard_phone_icon')
        cleaver.score('web_xray_dashboard_web_icon')

    if request.path == '/xray/experiments/':
        cleaver.score('web_xray_dashboard_experiments_icon')

    return experiments
