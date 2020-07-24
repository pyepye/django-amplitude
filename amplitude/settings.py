from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

API_KEY = getattr(settings, 'AMPLITUDE_API_KEY')
if not API_KEY:
    raise ImproperlyConfigured('"AMPLITUDE_API_KEY" is not set')

INCLUDE_USER_DATA = getattr(settings, 'AMPLITUDE_INCLUDE_USER_DATA', False)  # NOQA: E501
INCLUDE_GROUP_DATA = getattr(settings, 'AMPLITUDE_INCLUDE_GROUP_DATA', False)  # NOQA: E501

installed_apps = getattr(settings, 'INSTALLED_APPS')
middleware = getattr(settings, 'MIDDLEWARE')
missing_session_settings = (
    'django.contrib.sessions' not in installed_apps
    or 'django.contrib.sessions.middleware.SessionMiddleware' not in middleware  # NOQA: E503, E501
)
if missing_session_settings:
    error = ('django.contrib.sessions must be included in INSTALLED_APPS and '
             'django.contrib.sessions.middleware.SessionMiddleware in '
             'MIDDLEWARE to be possible to track users')
    raise ImproperlyConfigured(error)

missing_auth_settings = (
    'django.contrib.auth' not in installed_apps
    or 'django.contrib.auth.middleware.AuthenticationMiddleware' not in middleware  # NOQA: E503, E501
)
if INCLUDE_USER_DATA and missing_auth_settings:
    error = ('django.contrib.auth must be in INSTALLED_APPS and '
             'django.contrib.auth.middleware.AuthenticationMiddleware in '
             'MIDDLEWARE when "AMPLITUDE_INCLUDE_USER_DATA" is turned on')
    raise ImproperlyConfigured(error)
if INCLUDE_GROUP_DATA and missing_auth_settings:
    error = ('django.contrib.auth must be in INSTALLED_APPS and '
             'django.contrib.auth.middleware.AuthenticationMiddleware in '
             'MIDDLEWARE when "AMPLITUDE_INCLUDE_GROUP_DATA" is turned on')
    raise ImproperlyConfigured(error)
