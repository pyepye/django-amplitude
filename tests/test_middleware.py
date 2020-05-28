from django.urls import reverse


def test_send_page_view_event(mocker, client):
    request = mocker.patch('amplitude.amplitude.httpx.request')
    client.get(reverse('home'))
    request.assert_called()


def test_send_page_view_event_logged_in_user(mocker, django_user_model, client):  # NOQA
    request = mocker.patch('amplitude.amplitude.httpx.request')
    username = "user"
    password = "pass"
    django_user_model.objects.create_user(username=username, password=password)
    client.login(username=username, password=password)
    client.get(reverse('home'))
    request.assert_called()
