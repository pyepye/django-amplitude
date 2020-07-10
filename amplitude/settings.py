from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

AMPLITUDE_API_KEY = getattr(settings, 'AMPLITUDE_API_KEY')
if not AMPLITUDE_API_KEY:
    raise ImproperlyConfigured('"AMPLITUDE_API_KEY" is not set')

AMPLITUDE_INCLUDE_USER_DATA = getattr(settings, 'AMPLITUDE_INCLUDE_USER_DATA', False)  # NOQA: E501
AMPLITUDE_INCLUDE_GROUP_DATA = getattr(settings, 'AMPLITUDE_INCLUDE_GROUP_DATA', False)  # NOQA: E501
