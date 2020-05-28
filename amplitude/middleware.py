from . import Amplitude

amplitude = Amplitude()


class SendPageViewEvent(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        amplitude.page_view_event(request)
        return self.get_response(request)
