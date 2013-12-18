"""RapidSMS app for web and SMS split test experiments & event tracking."""

# import signal receivers here so they are sure
# to be registered before any signals are emitted
# ignore ImportError (TODO or any other...) exception
# that may be thrown when running setup.py

try:
    import listeners
except Exception:
    pass

__version_info__ = {
    'major': 0,
    'minor': 5,
    'micro': 9,
    'releaselevel': 'beta',
    'serial': 0
}


def get_version(short=False):
    assert __version_info__['releaselevel'] in ('alpha', 'beta', 'final')
    vers = ["%(major)i.%(minor)i" % __version_info__, ]
    if __version_info__['micro']:
        vers.append(".%(micro)i" % __version_info__)
    if __version_info__['releaselevel'] != 'final' and not short:
        vers.append('%s%i' % (__version_info__['releaselevel'][0],
                              __version_info__['serial']))
    return ''.join(vers)

__version__ = get_version()
