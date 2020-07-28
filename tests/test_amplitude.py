from importlib import reload
from time import time
from uuid import uuid4

import pytest
from django.contrib.auth.models import Group
from django.contrib.sessions.middleware import SessionMiddleware
from django.http import HttpRequest
from django.urls import reverse
from django.utils import translation
from httpx import HTTPError

from amplitude import Amplitude, settings
from amplitude.amplitude import AmplitudeException

from .fixtures import user  # NOQA: F401

amplitude = Amplitude()


def test_init_django_settings():
    amplitude = Amplitude()
    assert amplitude.api_key == settings.API_KEY
    assert amplitude.include_user_data == settings.INCLUDE_USER_DATA
    assert amplitude.include_group_data == settings.INCLUDE_GROUP_DATA


def test_init_pass_args():
    api_key = 'test_init_fake'
    amplitude = Amplitude(
        api_key=api_key,
        include_user_data=(not settings.INCLUDE_USER_DATA),
        include_group_data=(not settings.INCLUDE_GROUP_DATA),
    )
    assert amplitude.api_key == api_key
    assert amplitude.include_user_data == (not settings.INCLUDE_USER_DATA)
    assert amplitude.include_group_data == (not settings.INCLUDE_GROUP_DATA)


def test_send_events(mocker):
    mock = mocker.Mock()
    mock.json.return_value = {
        'code': 200,
        'server_upload_time': 1111111111111,
        'payload_size_bytes': 111,
        'events_ingested': 1
    }
    request = mocker.patch(
        'amplitude.amplitude.httpx.request', return_value=mock
    )
    events = [{'fake': {'fake': 'fake'}}]
    response = amplitude.send_events(events)
    assert isinstance(response, dict)
    kwargs = {
        'url': 'https://api.amplitude.com/2/httpapi',
        'method': 'POST',
        'json': {
            'events': events,
            'api_key': settings.API_KEY,
        }
    }
    request.assert_called_once_with(**kwargs)


def test_send_events_httpx_error(mocker):
    mock = mocker.Mock()
    mock.raise_for_status.side_effect = HTTPError()
    mocker.patch('amplitude.amplitude.httpx.request', return_value=mock)

    amplitude = Amplitude()
    with pytest.raises(AmplitudeException):
        amplitude.send_events([{}])


def test_build_event_data(freezer, rf):
    freezer.move_to('2002-01-01T00:00:00')

    amplitude_device_id = str(uuid4())
    amplitude_session_id = int(time()) * 1000
    laguage_code = 'en-GB'
    translation.activate(laguage_code)

    url_name = 'test_variable'
    param_key = 'testkey'
    param_value = 'testvalue'
    url = reverse(url_name, kwargs={'test': 'test'})
    content_type = 'application/json'
    content_length = 1234
    host = 'docs.djangoproject.dev:8000'
    accept = '*/*'
    accept_encoding = 'gzip'
    accept_language = 'en-GB'
    referrer = 'https://example.com/test/'
    request = rf.get(
        f'{url}?{param_key}={param_value}',
        CONTENT_TYPE=content_type,
        CONTENT_LENGTH=content_length,
        HTTP_HOST=host,
        HTTP_ACCEPT=accept,
        HTTP_ACCEPT_ENCODING=accept_encoding,
        HTTP_ACCEPT_LANGUAGE=accept_language,
        HTTP_REFERER=referrer,
    )

    middleware = SessionMiddleware()
    middleware.process_request(request)

    request.LANGUAGE_CODE = laguage_code
    request.session['amplitude_device_id'] = amplitude_device_id
    request.session['amplitude_session_id'] = amplitude_session_id
    request.session.save()

    event_type = 'some event'
    event = amplitude.build_event_data(
        request=request,
        event_type=event_type,
    )
    event_data = {
        'device_id': amplitude_device_id,
        'event_type': event_type,
        'time': 1009843200000,
        'ip': '127.0.0.1',
        'language': laguage_code,
        'event_properties': {
            'content_length': content_length,
            'content_params': {},
            'content_type': content_type,
            'http_accept': accept,
            'http_accept_encoding': accept_encoding,
            'http_accept_language': accept_language,
            'http_host': host,
            'method': 'GET',
            'params': {param_key: [param_value]},
            'referer': referrer,
            'scheme': 'http',
            'server_name': 'testserver',
            'server_port': '80',
            'url': url,
            'url_name': url_name
        },
        'adid': None,
        'android_id': None,
        'app_version': None,
        'carrier': None,
        'device_manufacturer': None,
        'device_model': None,
        'dma': None,
        'event_id': None,
        'idfa': None,
        'idfv': None,
        'insert_id': None,
        'os_name': 'Other',
        'os_version': '',
        'platform': 'Other',
        'price': None,
        'productId': None,
        'quantity': None,
        'revenue': None,
        'revenueType': None,
        'session_id': 1009843200000,
        'user_properties': {},
        'groups': [],
    }
    assert event == event_data


def test_build_event_data_with_kwargs(rf):
    request = rf.get('/')
    middleware = SessionMiddleware()
    middleware.process_request(request)
    request.session.save()

    event_properties = {'test': 'test'}
    app_version = 'app_version'
    carrier = 'carrier'
    dma = 'dma'
    price = 'price'
    quantity = 'quantity'
    revenue = 'revenue'
    productId = 'productId'
    revenueType = 'revenueType'
    idfa = 'idfa'
    idfv = 'idfv'
    adid = 'adid'
    android_id = 'android_id'
    event_id = 'event_id'
    insert_id = 'insert_id'
    event = amplitude.build_event_data(
        request=request,
        event_type='event type',
        event_properties=event_properties,
        app_version=app_version,
        carrier=carrier,
        dma=dma,
        price=price,
        quantity=quantity,
        revenue=revenue,
        productId=productId,
        revenueType=revenueType,
        idfa=idfa,
        idfv=idfv,
        adid=adid,
        android_id=android_id,
        event_id=event_id,
        insert_id=insert_id,
    )
    assert event['event_properties'] == event_properties
    assert event['app_version'] == app_version
    assert event['carrier'] == carrier
    assert event['dma'] == dma
    assert event['price'] == price
    assert event['quantity'] == quantity
    assert event['revenue'] == revenue
    assert event['productId'] == productId
    assert event['revenueType'] == revenueType
    assert event['idfa'] == idfa
    assert event['idfv'] == idfv
    assert event['adid'] == adid
    assert event['android_id'] == android_id
    assert event['event_id'] == event_id
    assert event['insert_id'] == insert_id


def test_clean_event():
    event = {
        '1': {
            '1': '1',
            '2': {},
            '3': '',
            '4': None,
            '5': [],
        },
        '2': {},
        '3': '',
        '4': None,
        '5': [],
        '6': '6',
    }
    cleaned_event = amplitude.clean_event(event=event)
    assert cleaned_event == {'1': {'1': '1'}, '6': '6'}


def test_event_properties_from_request(rf):
    url_name = 'test_variable'
    param_key = 'testkey'
    param_value = 'testvalue'
    url = reverse(url_name, kwargs={'test': 'test'})
    content_type = 'application/json'
    content_length = 1234
    host = 'docs.djangoproject.dev:8000'
    accept = '*/*'
    accept_encoding = 'gzip'
    accept_language = 'en-GB'
    referrer = 'https://example.com/test/'
    request = rf.get(
        f'{url}?{param_key}={param_value}',
        CONTENT_TYPE=content_type,
        CONTENT_LENGTH=content_length,
        HTTP_HOST=host,
        HTTP_ACCEPT=accept,
        HTTP_ACCEPT_ENCODING=accept_encoding,
        HTTP_ACCEPT_LANGUAGE=accept_language,
        HTTP_REFERER=referrer,
    )
    event_data = amplitude.event_properties_from_request(request=request)
    data = {
        'content_length': content_length,
        'content_params': {},
        'content_type': content_type,
        'http_accept': accept,
        'http_accept_encoding': accept_encoding,
        'http_accept_language': accept_language,
        'http_host': host,
        'method': 'GET',
        'params': {param_key: [param_value]},
        'referer': referrer,
        'scheme': 'http',
        'server_name': 'testserver',
        'server_port': '80',
        'url': url,
        'url_name': url_name
    }
    assert event_data == data


def test_user_properties_from_request(freezer, rf, user):  # NOQA: F811
    freezer.move_to('2002-01-01T00:00:00')

    usr = user()
    request = rf.get('/')
    request.user = usr
    user_data = {
        'date_joined': '2002-01-01T00:00:00',
        'email': usr.email,
        'full_name': f'{usr.first_name} {usr.last_name}',
        'is_staff': False,
        'is_superuser': False,
        'last_login': '2002-01-01T00:00:00',
        'username': usr.username
    }
    user_proerties = amplitude.user_properties_from_request(request=request)
    assert user_proerties == user_data


def test_user_properties_from_request_unauthenticated(rf, settings):
    request = rf.get('/')
    user_data = amplitude.user_properties_from_request(request=request)
    assert user_data == {}


def test_user_properties_from_request_setting_off(rf, settings, user):  # NOQA: F811, E501
    settings.AMPLITUDE_INCLUDE_USER_DATA = False
    from amplitude import settings as appsettings
    reload(appsettings)
    amplitude = Amplitude()

    usr = user()
    request = rf.get('/')
    request.user = usr
    user_data = amplitude.user_properties_from_request(request=request)
    assert user_data == {}


def test_group_from_request(freezer, rf, user):  # NOQA: F811
    usr = user()
    group_name = 'new_group'
    group = Group.objects.create(name=group_name)
    group.user_set.add(usr)

    request = rf.get('/')
    request.user = usr
    groups = [group_name]

    group_data = amplitude.group_from_request(request=request)
    assert group_data == groups


def test_group_from_request_unauthenticated(rf, settings):
    request = rf.get('/')
    group_data = amplitude.group_from_request(request=request)
    assert group_data == []


def test_group_from_request_setting_off(rf, settings, user):  # NOQA: F811
    settings.AMPLITUDE_INCLUDE_GROUP_DATA = False
    from amplitude import settings as appsettings
    reload(appsettings)
    amplitude = Amplitude()

    usr = user()
    request = rf.get('/')
    request.user = usr

    group_data = amplitude.group_from_request(request=request)
    assert group_data == []


def test_device_data_from_request(rf):
    request = rf.get('/')
    device_data = amplitude.device_data_from_request(request=request)
    test_data = {
        'device_manufacturer': None,
        'device_model': None,
        'os_name': 'Other',
        'os_version': '',
        'platform': 'Other',
    }
    assert device_data == test_data


def test_device_data_from_request_known_user_agent(rf):
    request = rf.get('/', HTTP_USER_AGENT='')
    device_data = amplitude.device_data_from_request(request=request)
    device_data_two = amplitude.device_data_from_request(request=request)
    assert device_data == device_data_two


def test_device_data_no_meta(rf):
    request = HttpRequest()
    delattr(request, 'META')
    device_data = amplitude.device_data_from_request(request=request)
    assert device_data == {}


def test_location_data_from_ip_address_no_meta(rf):
    location_data = amplitude.location_data_from_ip_address(ip_address='')
    assert location_data == {}
