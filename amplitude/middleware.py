import logging
from time import time
from uuid import uuid4

from django.urls import resolve

from . import Amplitude, settings
from .amplitude import AmplitudeException

log = logging.getLogger(__name__)
amplitude = Amplitude()


class SessionInfo(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.session.get('amplitude_device_id'):
            request.session['amplitude_device_id'] = str(uuid4())
        if not request.session.get('amplitude_session_id'):
            request.session['amplitude_session_id'] = int(time()) * 1000
        return self.get_response(request)


class SendPageViewEvent(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Ignore URLs can be either a url path or url name
        if request.path_info in settings.IGNORE_URLS:
            return self.get_response(request)
        current_url = resolve(request.path_info)
        if current_url.url_name in settings.IGNORE_URLS:
            return self.get_response(request)

        event = amplitude.build_event_data(
            event_type='Page view', request=request
        )
        try:
            amplitude.send_events(events=[event])
        except AmplitudeException as e:
            log.error(f'Unable to send page view event due to - {e}')
        return self.get_response(request)
