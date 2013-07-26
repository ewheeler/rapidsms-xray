
def web_experiments(request):
    cleaver = request.environ['cleaver']

    experiments = {}

    experiments['web_dashboard_background_color_experiment'] = cleaver(
        'web_dashboard_background_color',
        ('white', '#FFFFFF'),
        ('grey', '#F3F3F3')
    )

    if request.path == '/patients/workspace/':
        cleaver.score('web_dashboard_background_color')

    experiments['web_dashboard_title_experiment'] = cleaver(
        'web_dashboard_title',
        ('RapidSMS 1000 Days', 'RapidSMS 1000 Days'),
        ('1000 Days', '1000 Days'),
        ('Thousand Days', 'Thousand Days')
    )

    if request.path == '/patients/workspace/':
        cleaver.score('web_dashboard_title')

    return experiments
