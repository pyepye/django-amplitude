from django.http.response import HttpResponse
from django.urls import path


def empty_view(request):
    return HttpResponse()


urlpatterns = [
    path('', empty_view, name='home'),
    path('test/', empty_view, name='test'),
    path('test/<test>', empty_view, name='test_variable'),
]
