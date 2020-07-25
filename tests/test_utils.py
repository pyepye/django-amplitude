from django.http import HttpRequest
from amplitude.utils import get_client_ip, get_user_agent


def test_get_client_ip(client, settings):
    if 'amplitude.middleware.SendPageViewEvent' in settings.MIDDLEWARE:
        settings.MIDDLEWARE.remove('amplitude.middleware.SendPageViewEvent')

    request = HttpRequest()
    get_client_ip(request)


def test_get_client_ip_no_meta(client, settings):
    if 'amplitude.middleware.SendPageViewEvent' in settings.MIDDLEWARE:
        settings.MIDDLEWARE.remove('amplitude.middleware.SendPageViewEvent')

    request = HttpRequest()
    delattr(request, 'META')
    ip = get_client_ip(request)
    assert ip == ''


def test_get_client_ip_x_forwarded_for(client, settings):
    if 'amplitude.middleware.SendPageViewEvent' in settings.MIDDLEWARE:
        settings.MIDDLEWARE.remove('amplitude.middleware.SendPageViewEvent')

    request = HttpRequest()
    correct_ip = '70.41.3.18'
    request.META['HTTP_X_FORWARDED_FOR'] = f'203.0.113.195, {correct_ip}'
    ip = get_client_ip(request)
    assert ip == correct_ip


def test_get_user_agent(client, settings):
    if 'amplitude.middleware.SendPageViewEvent' in settings.MIDDLEWARE:
        settings.MIDDLEWARE.remove('amplitude.middleware.SendPageViewEvent')

    request = HttpRequest()
    request.META['HTTP_USER_AGENT'] = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:15.0) Gecko/20100101 Firefox/15.0.1'  # NOQA: E501
    user_agent = get_user_agent(request)
    assert str(user_agent) == 'PC / Ubuntu / Firefox 15.0.1'


def test_get_user_agent_no_meta(client, settings):
    if 'amplitude.middleware.SendPageViewEvent' in settings.MIDDLEWARE:
        settings.MIDDLEWARE.remove('amplitude.middleware.SendPageViewEvent')

    request = HttpRequest()
    delattr(request, 'META')
    user_agent = get_user_agent(request)
    assert user_agent == ''


def test_get_user_agent_no_http_user_agent(client, settings):
    if 'amplitude.middleware.SendPageViewEvent' in settings.MIDDLEWARE:
        settings.MIDDLEWARE.remove('amplitude.middleware.SendPageViewEvent')

    request = HttpRequest()
    user_agent = get_user_agent(request)
    assert str(user_agent) == 'Other / Other / Other'


def test_get_user_agent_known_user_agent(client, settings):
    if 'amplitude.middleware.SendPageViewEvent' in settings.MIDDLEWARE:
        settings.MIDDLEWARE.remove('amplitude.middleware.SendPageViewEvent')

    request = HttpRequest()
    request.META['HTTP_USER_AGENT'] = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:15.0) Gecko/20100101 Firefox/15.0.1'  # NOQA: E501
    get_user_agent(request)
    user_agent = get_user_agent(request)
    assert str(user_agent) == 'PC / Ubuntu / Firefox 15.0.1'
