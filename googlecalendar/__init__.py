from django.conf import settings

if not hasattr(settings, 'USER_ADD_EVENTS'):
    settings.USER_ADD_EVENTS = False

__version__ = (1, 2)
def get_version():
    return '.'.join(map(str, __version__))
