from importlib import reload
from urllib.parse import urlencode

from django.conf import settings
from django.urls import reverse
from httpx import HTTPError

from .fixtures import user  # NOQA: F401

AMPLITUDE_URL = 'https://api.amplitude.com/2/httpapi'


def test_send_page_view_event(mocker, client, freezer):
    freezer.move_to('2002-01-01T00:00:00')

    request = mocker.patch('amplitude.amplitude.httpx.request')
    uid = mocker.patch('amplitude.middleware.uuid4')
    fakeuuid = '1234abcd'
    uid.return_value = fakeuuid

    url_name = 'test_home'
    url = reverse(url_name)
    client.get(url)
    events = [{
        'event_properties': {
            'method': 'GET',
            'url': url,
            'url_name': url_name,
            'scheme': 'http',
            'server_name': 'testserver',
            'server_port': '80',
        },
        'device_id': fakeuuid,
        'event_type': 'Page view',
        'ip': '127.0.0.1',
        'os_name': 'Other',
        'platform': 'Other',
        'session_id': 1009843200000,
        'time': 1009843200000,
    }]

    kwargs = {
        'url': AMPLITUDE_URL,
        'method': 'POST',
        'json': {
            'events': events,
            'api_key': settings.AMPLITUDE_API_KEY,
        }
    }
    request.assert_called_once_with(**kwargs)
    freezer.move_to('2002-01-01T00:00:01')
    url_name2 = 'test'
    url2 = reverse(url_name2)
    client.get(url2)
    events[0]['event_properties']['url'] = url2
    events[0]['event_properties']['url_name'] = url_name2
    events[0]['event_type'] = 'Page view'
    events[0]['time'] = 1009843201000
    kwargs['json']['events'] = events
    request.assert_any_call(**kwargs)


def test_send_page_view_event_logged_in_user(
    mocker, client, freezer, user, django_user_model  # NOQA: F811
):
    freezer.move_to('2002-01-01T00:00:00')

    request = mocker.patch('amplitude.amplitude.httpx.request')
    usr = user()
    client.force_login(usr)

    url_name = 'test_home'
    url = reverse(url_name)
    user_id = django_user_model.objects.get(username=usr.username).pk
    events = [{
        'event_properties': {
            'method': 'GET',
            'url': url,
            'url_name': url_name,
            'scheme': 'http',
            'server_name': 'testserver',
            'server_port': '80',
        },
        'device_id': mocker.ANY,
        'event_type': 'Page view',
        'ip': '127.0.0.1',
        'os_name': 'Other',
        'platform': 'Other',
        'session_id': 1009843200000,
        'time': 1009843200000,  # 2002-01-01
        'user_id': f'{user_id:05}',
        'user_properties': {
            'date_joined': '2002-01-01T00:00:00',
            'email': usr.email,
            'full_name': f'{usr.first_name} {usr.last_name}',
            'is_staff': False,
            'is_superuser': False,
            'last_login': '2002-01-01T00:00:00',
            'username': usr.username
        },
    }]

    kwargs = {
        'url': AMPLITUDE_URL,
        'method': 'POST',
        'json': {
            'events': events,
            'api_key': settings.AMPLITUDE_API_KEY,
        }
    }
    client.get(url)
    request.assert_called_once_with(**kwargs)


def test_send_page_view_event_with_url_params(mocker, client, freezer):
    freezer.move_to('2002-01-01T00:00:00')

    request = mocker.patch('amplitude.amplitude.httpx.request')
    a_value_one = 'avalue space'
    a_value_two = 'avalue+plus'
    b_value_one = 'bvalue'
    params_url = [
        ('a', a_value_one),
        ('a', a_value_two),
        ('b', b_value_one),
    ]
    params = {
        'a': [a_value_one, a_value_two],
        'b': [b_value_one],
    }

    url_name = 'test_home'
    url = reverse(url_name)
    query = urlencode(params_url)
    params_url = f'{url}?{query}'

    events = [{
        'event_properties': {
            'method': 'GET',
            'params': params,
            'url': url,
            'url_name': url_name,
            'scheme': 'http',
            'server_name': 'testserver',
            'server_port': '80',
        },
        'device_id': mocker.ANY,
        'event_type': 'Page view',
        'ip': '127.0.0.1',
        'os_name': 'Other',
        'platform': 'Other',
        'session_id': 1009843200000,
        'time': 1009843200000,  # 2002-01-01
    }]

    kwargs = {
        'url': AMPLITUDE_URL,
        'method': 'POST',
        'json': {
            'events': events,
            'api_key': settings.AMPLITUDE_API_KEY,
        }
    }

    client.get(params_url)
    request.assert_called_once_with(**kwargs)


def test_send_page_view_event_no_auth_middleware(
    mocker, settings, client, freezer
):
    settings.INSTALLED_APPS.remove('django.contrib.auth')
    settings.MIDDLEWARE.remove(
        'django.contrib.auth.middleware.AuthenticationMiddleware')
    settings.AMPLITUDE_INCLUDE_USER_DATA = False
    settings.AMPLITUDE_INCLUDE_GROUP_DATA = False
    from amplitude import settings as appsettings
    reload(appsettings)

    freezer.move_to('2002-01-01T00:00:00')

    request = mocker.patch('amplitude.amplitude.httpx.request')
    url_name = 'test_home'
    url = reverse(url_name)
    events = [{
        'event_properties': {
            'method': 'GET',
            'url': url,
            'url_name': url_name,
            'scheme': 'http',
            'server_name': 'testserver',
            'server_port': '80',
        },
        'device_id': mocker.ANY,
        'event_type': 'Page view',
        'ip': '127.0.0.1',
        'os_name': 'Other',
        'platform': 'Other',
        'session_id': 1009843200000,
        'time': 1009843200000,    # 2002-01-01
    }]

    kwargs = {
        'url': AMPLITUDE_URL,
        'method': 'POST',
        'json': {
            'events': events,
            'api_key': settings.AMPLITUDE_API_KEY,
        }
    }

    client.get(url)
    request.assert_called_once_with(**kwargs)


def test_send_page_view_event_httpx_error(mocker, client):
    mock = mocker.Mock()
    mock.raise_for_status.side_effect = HTTPError('')
    mocker.patch('amplitude.amplitude.httpx.request', return_value=mock)
    client.get('')


def test_middleware_ignore_url(mocker, settings, client):
    url_name = 'test_home'
    url = reverse(url_name)
    settings.AMPLITUDE_IGNORE_URLS = [url]
    settings.AMPLITUDE_INCLUDE_USER_DATA = False
    settings.AMPLITUDE_INCLUDE_GROUP_DATA = False
    from amplitude import settings as appsettings
    reload(appsettings)

    build_event_data = mocker.patch(
        'amplitude.middleware.amplitude.build_event_data'
    )
    client.get(url)
    build_event_data.assert_not_called()


def test_middleware_ignore_url_name(mocker, settings, client):
    url_name = 'test_home'
    settings.AMPLITUDE_IGNORE_URLS = [url_name]
    settings.AMPLITUDE_INCLUDE_USER_DATA = False
    settings.AMPLITUDE_INCLUDE_GROUP_DATA = False
    from amplitude import settings as appsettings
    reload(appsettings)

    build_event_data = mocker.patch(
        'amplitude.middleware.amplitude.build_event_data'
    )
    url = reverse(url_name)
    client.get(url)
    build_event_data.assert_not_called()
