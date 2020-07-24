from urllib.parse import urlencode

from django.conf import settings
from django.urls import reverse

AMPLITUDE_URL = 'https://api.amplitude.com/2/httpapi'


def test_send_page_view_event(mocker, client, freezer):
    freezer.move_to('2002-01-01T00:00:00')

    request = mocker.patch('amplitude.amplitude.httpx.request')
    url_name = 'test_home'
    url = reverse(url_name)
    events = [{
        'event_properties': {
            'method': 'GET',
            'params': {},
            'url': url,
            'url_name': url_name
        },
        'event_type': f'Page view {url_name}',
        'ip': '127.0.0.1',
        'os_name': 'Other',
        'platform': 'Other',
        'session_id': 1009843200000,
        'time': 1009843200000,
        'user_id': 1009843200000,  # 2002-01-01
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


def test_send_page_view_event_logged_in_user(
    mocker, client, freezer, django_user_model
):
    freezer.move_to('2002-01-01T00:00:00')

    request = mocker.patch('amplitude.amplitude.httpx.request')
    username = 'user'
    email = 'test@example.com'
    password = 'pass'
    first_name = 'Test'
    last_name = 'User'
    django_user_model.objects.create_user(
        username=username,
        password=password,
        email=email,
        first_name=first_name,
        last_name=last_name,
    )
    client.login(username=username, password=password)

    url_name = 'test_home'
    url = reverse(url_name)
    user_id = django_user_model.objects.get(username=username).pk
    events = [{
        'event_properties': {
            'method': 'GET',
            'params': {},
            'url': url,
            'url_name': url_name
        },
        'event_type': f'Page view {url_name}',
        'ip': '127.0.0.1',
        'os_name': 'Other',
        'platform': 'Other',
        'session_id': 1009843200000,
        'time': 1009843200000,  # 2002-01-01
        'user_id': f'{user_id:05}',
        'user_properties': {
            'date_joined': '2002-01-01T00:00:00',
            'email': email,
            'full_name': f'{first_name} {last_name}',
            'is_staff': False,
            'is_superuser': False,
            'last_login': '2002-01-01T00:00:00',
            'username': username
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
            'url_name': url_name
        },
        'event_type': f'Page view {url_name}',
        'ip': '127.0.0.1',
        'os_name': 'Other',
        'platform': 'Other',
        'session_id': 1009843200000,
        'time': 1009843200000,  # 2002-01-01
        'user_id': 1009843200000,  # 2002-01-01
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
