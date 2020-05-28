import logging
import time
from typing import List

import httpx
from django.conf import settings
from django.urls import resolve

try:
    from user_agents import parse as user_agent_parse
except ImportError:  # pragma: no cover
    CAN_USER_AGENT = False
else:
    KNOWN_USER_AGENTS = {}
    CAN_USER_AGENT = True

try:
    from django.contrib.gis.geoip2 import GeoIP2
except ImportError:
    CAN_GEOIP = False
else:  # pragma: no cover
    CAN_GEOIP = True


log = logging.getLogger(__name__)


class AmplitudeException(Exception):
    pass


class Amplitude():

    def __init__(
        self,
        api_key: str = None,
        include_user_data: bool = False,
        include_group_data: bool = False,
    ):
        if not api_key:
            api_key = settings.AMPLITUDE_API_KEY

        self.url = 'https://api.amplitude.com/2/httpapi'
        self.api_key = api_key
        self.include_user_data = include_user_data
        self.include_group_data = include_group_data

    def page_view_event(self, request):
        """
        Send an event based on a Django request
        """
        url_name = resolve(request.path_info).url_name
        event_data = {
            'user_id': request.user.id,
            'event_type': f'Page view {url_name}',
            "time": time.time(),
            # 'app_version': '',
            # 'carrier': '',
            # 'price': '',
            # 'quantity': '',
            # 'revenue': '',
            # 'productId': '',
            # 'revenueType': '',
            'ip': get_client_ip(request),
            # 'event_id': '',
            # 'insert_id': '',
        }

        if request.session:
            event_data['session_id'] = request.session.session_key

        event_data['event_properties'] = {
            'url': request.path_info,
            'url_name': url_name,
            'method': request.method,
            'params': dict(request.GET)
        }
        if request.resolver_match:
            event_data['event_properties']['kwargs'] = request.resolver_match.kwargs    # NOQA: E501

        LANGUAGE_CODE = getattr(request, "LANGUAGE_CODE", '')
        if LANGUAGE_CODE:
            event_data['language'] = LANGUAGE_CODE

        if event_data['ip'] and CAN_GEOIP:
            ip_address = event_data['ip']
            # pip install geoip2
            # https://pypi.org/project/geoip2/
            # from django.contrib.gis.geoip2 import GeoIP2
            g = GeoIP2()
            location = g.city(ip_address)
            event_data['country'] = location['country_name']
            event_data['city'] = location['city']
            event_data['region'] = g.region(ip_address)
            lat_lon = g.lat_lon(ip_address)
            event_data['location_lat'] = lat_lon[0]
            event_data['location_lng'] = lat_lon[1]

        if CAN_USER_AGENT:
            user_agent = get_user_agent(request)
            if user_agent:
                event_data['os_name'] = user_agent.os.family
                event_data['os_version'] = user_agent.os.version_string
                event_data['platform'] = user_agent.device.family
                # event_data['device_brand']
                event_data['device_manufacturer'] = user_agent.device.brand
                event_data['device_model'] = user_agent.device.model

        if self.include_group_data and request.user.is_authenticated:
            event_data['user_properties'] = {
                'username': request.user.get_username(),
                'email': request.user.username,
                'full_name': request.user.get_full_name(),
                'is_staff': request.user.is_staff,
                'is_superuser': request.user.is_superuser,
                'last_login': request.user.last_login.isoformat(),
                'date_joined': request.user.date_joined.isoformat(),
            }
        if self.include_group_data and request.user.is_authenticated:
            event_data['groups'] = list(request.user.groups.all().values_list('name', flat=True))  # NOQA

        self.send_events(events=[event_data])

    def send_events(self, events: List[dict]) -> dict:
        """
        https://developers.amplitude.com/docs/http-api-v2
        """
        kwargs = {
            'url': self.url,
            'method': 'POST',
            'json': {
                'event': events,
                'api_key': self.api_key
            }
        }
        response = httpx.request(**kwargs)
        try:
            response.raise_for_status()
        except httpx.HTTPError as e:
            raise AmplitudeException(e)

        return response.json()


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[-1].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_user_agent(request):
    if not hasattr(request, 'META'):
        return ''

    http_user_agent = request.META.get('HTTP_USER_AGENT', '')
    if http_user_agent:
        return ''

    if http_user_agent in KNOWN_USER_AGENTS:
        return KNOWN_USER_AGENTS[http_user_agent]

    user_agent = user_agent_parse(http_user_agent)
    KNOWN_USER_AGENTS[http_user_agent] = user_agent

    return user_agent
