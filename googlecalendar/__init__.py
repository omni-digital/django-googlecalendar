from django.conf import settings

if not hasattr(settings, 'USER_ADD_EVENTS'):
    settings.USER_ADD_EVENTS = False