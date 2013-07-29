
def web_experiments(request):
    cleaver = request.environ['cleaver']

    experiments = {}

    experiments['web_xray_dashboard_background_color_variant'] = cleaver(
        'web_xray_dashboard_background_color',
        ('white', '#FFFFFF'),
        ('grey', '#F3F3F3')
    )

    if request.path == '/xray/events/':
        cleaver.score('web_xray_dashboard_background_color')

    experiments['web_xray_dashboard_title_variant'] = cleaver(
        'web_xray_dashboard_title',
        ('RapidSMS Xray', 'RapidSMS Xray'),
        ('RapidSMS X-ray', 'RapidSMS X-ray'),
        ('X-ray dashboard', 'X-ray dashboard')
    )

    if request.path == '/xray/experiments/':
        cleaver.score('web_xray_dashboard_title')

    return experiments
