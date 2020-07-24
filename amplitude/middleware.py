from time import time
from uuid import uuid4

from . import Amplitude

amplitude = Amplitude()


class SendPageViewEvent(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.session.get('amplitude_device_id'):
            request.session['amplitude_device_id'] = str(uuid4())
        if not request.session.get('amplitude_session_id'):
            request.session['amplitude_session_id'] = int(time()) * 1000

        amplitude.page_view_event(request)
        return self.get_response(request)
