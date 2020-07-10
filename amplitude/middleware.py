from . import Amplitude

amplitude = Amplitude()


class SendPageViewEvent(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            """
            Catches 'WSGIRequest' object has no attribute 'user' or 'session'
            if django.contrib.auth or django.contrib.sessions not in INSTALLED_APPS
            """  # NOQA: E501
            amplitude.page_view_event(request)
        except AttributeError:
            pass
        return self.get_response(request)
