import logging
import time
from typing import Any, Dict, List

import httpx
from django.contrib.auth import get_user_model
from django.http import HttpRequest
from django.urls import resolve

from . import settings as app_settings
from .utils import get_client_ip, get_user_agent

try:
    from django.contrib.gis.geoip2 import GeoIP2  # type: ignore
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
        include_user_data: bool = None,
        include_group_data: bool = None,
    ):
        if not api_key:
            api_key = app_settings.API_KEY
        if include_user_data is None:
            include_user_data = app_settings.INCLUDE_USER_DATA
        if include_group_data is None:
            include_group_data = app_settings.INCLUDE_GROUP_DATA

        self.url = 'https://api.amplitude.com/2/httpapi'
        self.api_key = api_key
        self.include_user_data = include_user_data
        self.include_group_data = include_group_data

    def send_events(self, events: List[Dict[str, Any]]) -> dict:
        """
        https://developers.amplitude.com/docs/http-api-v2
        """
        events = [self.clean_event(event) for event in events]
        kwargs: Dict[str, Any] = {
            'url': self.url,
            'method': 'POST',
            'json': {
                'events': events,
                'api_key': self.api_key
            }
        }
        response = httpx.request(**kwargs)
        try:
            response.raise_for_status()
        except httpx.HTTPError as e:
            raise AmplitudeException(e)

        return response.json()

    def clean_event(self, event: dict) -> dict:
        for key, value in event.items():
            if isinstance(value, dict):
                event[key] = {k: v for k, v in value.items() if v is not [None, [], '', {}]}  # NOQA: E501

        event = {k: v for k, v in event.items() if v not in [None, [], '', {}]}

        return event

    def build_event_data(
        self, event_type: str, request: HttpRequest, **kwargs
    ) -> dict:
        """
        Build event data using a Django request object
        """
        event: Dict[str, Any] = {
            'device_id': request.session.get('amplitude_device_id'),
            'event_type': event_type,
            'time': int(round(time.time() * 1000)),
            'ip': get_client_ip(request),
            'language': getattr(request, 'LANGUAGE_CODE', ''),
            'app_version': kwargs.get('app_version'),
            'carrier': kwargs.get('carrier'),
            'dma': kwargs.get('dma'),
            'price': kwargs.get('price'),
            'quantity': kwargs.get('quantity'),
            'revenue': kwargs.get('revenue'),
            'productId': kwargs.get('productId'),
            'revenueType': kwargs.get('revenueType'),
            'idfa': kwargs.get('idfa'),
            'idfv': kwargs.get('idfv'),
            'adid': kwargs.get('adid'),
            'android_id': kwargs.get('android_id'),
            'event_id': kwargs.get('event_id'),
            'insert_id': kwargs.get('insert_id'),
        }
        try:
            event['user_id'] = f'{request.user.pk:05}'
        except (AttributeError, TypeError):
            pass

        event['session_id'] = request.session.get('amplitude_session_id')
        event['event_properties'] = self.event_properties_from_request(request)
        event['user_properties'] = self.user_properties_from_request(request)
        event['groups'] = self.group_from_request(request)
        device_data = self.device_data_from_request(request)
        event.update(device_data)
        location_data = self.location_data_from_ip_address(event['ip'])
        event.update(location_data)
        return event

    def event_properties_from_request(self, request: HttpRequest) -> dict:
        url_name = resolve(request.path_info).url_name
        event_properties = {
            'url': request.path,
            'url_name': url_name,
            'method': request.method,
            'params': dict(request.GET),
        }
        if request.resolver_match:
            event_properties['kwargs'] = request.resolver_match.kwargs
        return event_properties

    def user_properties_from_request(self, request: HttpRequest) -> dict:
        try:
            request.user.is_authenticated
        except AttributeError:
            return {}

        if not self.include_user_data or not request.user.is_authenticated:
            return {}

        User = get_user_model()
        user = User.objects.get(pk=request.user.pk)

        return {
            'username': user.get_username(),
            'email': user.email,
            'full_name': user.get_full_name(),
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser,
            'last_login': user.last_login.isoformat(),
            'date_joined': user.date_joined.isoformat(),
        }

    def group_from_request(self, request: HttpRequest) -> list:
        try:
            request.user.is_authenticated
        except AttributeError:
            return []

        if not self.include_group_data or not request.user.is_authenticated:
            return []

        User = get_user_model()
        user = User.objects.get(pk=request.user.pk)
        groups = user.groups.all().values_list('name', flat=True)
        return list(groups)

    def location_data_from_ip_address(self, ip_address: str) -> dict:
        location_data: dict = {}

        if not ip_address or not CAN_GEOIP:
            return location_data

        # pip install geoip2
        # https://pypi.org/project/geoip2/
        # from django.contrib.gis.geoip2 import GeoIP2
        g = GeoIP2()
        location = g.city(ip_address)
        location_data['country'] = location['country_name']
        location_data['city'] = location['city']
        location_data['region'] = g.region(ip_address)
        lat_lon = g.lat_lon(ip_address)
        location_data['location_lat'] = lat_lon[0]
        location_data['location_lng'] = lat_lon[1]
        return location_data

    def device_data_from_request(self, request: HttpRequest) -> dict:
        device_data: dict = {}

        user_agent = get_user_agent(request)
        if not user_agent:
            return device_data

        device_data['os_name'] = user_agent.os.family
        device_data['os_version'] = user_agent.os.version_string
        device_data['platform'] = user_agent.device.family
        # device_data['device_brand']
        device_data['device_manufacturer'] = user_agent.device.brand
        device_data['device_model'] = user_agent.device.model
        return device_data
