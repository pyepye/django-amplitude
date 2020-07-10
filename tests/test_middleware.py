from urllib.parse import urlencode

from django.conf import settings
from django.urls import reverse

AMPLITUDE_URL = 'https://api.amplitude.com/2/httpapi'


def test_send_page_view_event(mocker, client, freezer):
    freezer.move_to('2002-01-01')  # 2002-01-01

    request = mocker.patch('amplitude.amplitude.httpx.request')
    url_name = 'home'
    url = reverse('home')
    event = [{
        'device_manufacturer': None,
        'device_model': None,
        'event_properties': {
            'method': 'GET',
            'params': {},
            'url': url,
            'url_name': url_name
        },
        'event_type': f'Page view {url_name}',
        'ip': '127.0.0.1',
        'os_name': 'Other',
        'os_version': '',
        'platform': 'Other',
        'session_id': None,
        'time': 1009843200.0,
        'user_id': None
    }]

    kwargs = {
        'url': AMPLITUDE_URL,
        'method': 'POST',
        'json': {
            'event': event,
            'api_key': settings.AMPLITUDE_API_KEY,
        }
    }

    client.get(reverse('home'))
    request.assert_called_once_with(**kwargs)


def test_send_page_view_event_logged_in_user(
    mocker, client, freezer, django_user_model
):
    freezer.move_to('2002-01-01')

    request = mocker.patch('amplitude.amplitude.httpx.request')
    username = 'user'
    password = 'pass'
    django_user_model.objects.create_user(username=username, password=password)
    client.login(username=username, password=password)

    url_name = 'home'
    url = reverse('home')
    user_id = django_user_model.objects.get(username=username).pk
    event = [{
        'device_manufacturer': None,
        'device_model': None,
        'event_properties': {
            'method': 'GET',
            'params': {},
            'url': url,
            'url_name': url_name
        },
        'event_type': f'Page view {url_name}',
        'ip': '127.0.0.1',
        'os_name': 'Other',
        'os_version': '',
        'platform': 'Other',
        'session_id': client.session.session_key,
        'time': 1009843200.0,  # 2002-01-01
        'user_id': user_id
    }]

    kwargs = {
        'url': AMPLITUDE_URL,
        'method': 'POST',
        'json': {
            'event': event,
            'api_key': settings.AMPLITUDE_API_KEY,
        }
    }

    client.get(url)
    request.assert_called_once_with(**kwargs)


def test_send_page_view_event_with_url_params(mocker, client, freezer):
    freezer.move_to('2002-01-01')

    request = mocker.patch('amplitude.amplitude.httpx.request')
    url_name = 'home'

    params_url = {
        'pname': 'This has a space',
        'pname2': 'This+has+a+plus',
    }

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

    query = urlencode(params_url)
    url = reverse('home')
    params_url = f'{url}?{query}'

    event = [{
        'device_manufacturer': None,
        'device_model': None,
        'event_properties': {
            'method': 'GET',
            'params': params,
            'url': url,
            'url_name': url_name
        },
        'event_type': f'Page view {url_name}',
        'ip': '127.0.0.1',
        'os_name': 'Other',
        'os_version': '',
        'platform': 'Other',
        'session_id': None,
        'time': 1009843200.0,  # 2002-01-01
        'user_id': None
    }]

    kwargs = {
        'url': AMPLITUDE_URL,
        'method': 'POST',
        'json': {
            'event': event,
            'api_key': settings.AMPLITUDE_API_KEY,
        }
    }

    client.get(params_url)
    request.assert_called_once_with(**kwargs)
