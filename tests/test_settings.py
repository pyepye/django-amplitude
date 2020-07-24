from importlib import reload

import pytest
from django.core.exceptions import ImproperlyConfigured


"""
ToDo: The pytest-django settings fixture appears to be module scope no function
"""


def test_missing_api_key(settings):
    settings.AMPLITUDE_API_KEY = None

    with pytest.raises(ImproperlyConfigured):
        from amplitude import settings as appsettings
        reload(appsettings)


def test_missing_sessions_app(settings):
    settings.INSTALLED_APPS.remove('django.contrib.sessions')
    with pytest.raises(ImproperlyConfigured):
        from amplitude import settings as appsettings
        reload(appsettings)
    settings.INSTALLED_APPS.append('django.contrib.sessions')


def test_missing_sessions_middleware(settings):
    settings.MIDDLEWARE.remove(
        'django.contrib.sessions.middleware.SessionMiddleware')
    with pytest.raises(ImproperlyConfigured):
        from amplitude import settings as appsettings
        reload(appsettings)
    settings.MIDDLEWARE.append(
        'django.contrib.sessions.middleware.SessionMiddleware')


def test_include_user_data_no_auth(settings):
    settings.AMPLITUDE_INCLUDE_USER_DATA = True
    settings.AMPLITUDE_INCLUDE_GROUP_DATA = False
    authmiddleware = 'django.contrib.auth.middleware.AuthenticationMiddleware'
    if authmiddleware in settings.MIDDLEWARE:
        settings.MIDDLEWARE.remove(authmiddleware)

    with pytest.raises(ImproperlyConfigured):
        from amplitude import settings as appsettings
        reload(appsettings)


def test_include_group_data_no_auth(settings):
    settings.AMPLITUDE_INCLUDE_USER_DATA = False
    settings.AMPLITUDE_INCLUDE_GROUP_DATA = True
    authmiddleware = 'django.contrib.auth.middleware.AuthenticationMiddleware'
    if authmiddleware in settings.MIDDLEWARE:
        settings.MIDDLEWARE.remove(authmiddleware)

    with pytest.raises(ImproperlyConfigured):
        from amplitude import settings as appsettings
        reload(appsettings)
