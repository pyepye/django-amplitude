# Django Amplitude

Integration between Django and [Amplitude.com](https://amplitude.com/) to help send events via the [Amplitude HTTP API (v2)](https://developers.amplitude.com/docs/http-api-v2)


## Quick start

### Installation

```bash
pip install django-amplitude
```

Add `amplitude` to your `INSTALLED_APPS`. If they are not already the Django `sessions` app must also be added:

```python
INSTALLED_APPS = [
    ...
    'django.contrib.sessions',
    ...
    'amplitude',
]
```

If you do not have it already you must also add the Django `django.contrib.sessions.middleware.SessionMiddleware`. Then add the ampliturde `SessionInfo` middleware after the `SessionMiddleware`:
```python
MIDDLEWARE = [
    ...
    'django.contrib.sessions.middleware.SessionMiddleware',
    ...
    'amplitude.middleware.SessionInfo',
]
```

Now set your Amplitude API key and user / group options in your `settings.py`:
```python
# Settings > Projects > <Your project> > General > API Key
AMPLITUDE_API_KEY = '<amplitude-project-api-key>'

# You can also choose if you want to include user and group data (Default False)
AMPLITUDE_INCLUDE_USER_DATA = False
AMPLITUDE_INCLUDE_GROUP_DATA = False
```

*Note: If you want to include user or group data you must ensure the [Django auth is setup correctly](https://docs.djangoproject.com/en/3.0/topics/auth/#installation). This includes adding `django.contrib.auth` and `django.contrib.contenttypes` to `INSTALLED_APPS` and `django.contrib.auth.middleware.AuthenticationMiddleware` to `MIDDLEWARE`*.


## Usage

### Page view events

If you want to send an event to Amplitude on every page view you can use the django-amplitude `SendPageViewEvent` middleware to your `MIDDLEWARE` in your Django settings.

This will automatically create an event called `Page view` with all the information it's possible to pull from the Django request object such as URL path and parameters, user agent info, IP info, user info etc.

It must be placed after the `amplitude.middleware.SessionInfo` middleware:

```python
MIDDLEWARE = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    ...
    'amplitude.middleware.SessionInfo',
    'amplitude.middleware.SendPageViewEvent',
]
```


### Sending events manually

If you want to send your own events:
```python
from amplitude import Amplitude

amplitude = Amplitude()
event_data = amplitude.build_event_data(
    event_type='Some event type',
    request=request,
)
amplitude.send_events([event_data])
```


### build_event_data missing event data keys

The `build_event_data` method (and in extension the `SendPageViewEvent` middleware) currently does not send the following keys from `UploadRequestBody` type in [Amplitude HTTP API (v2)](https://developers.amplitude.com/docs/http-api-v2):

* event_id
* app_version
* carrier
* price
* quantity
* revenue
* productId
* revenueType
* idfa
* idfv
* adid
* android_id
* dma
* insert_id

If you want to record an event in Amplitude with any of these keys you must use build and send your own event data using `amplitude.build_event_data` where you can pass any of the above as kwargs:

```python
amplitude = Amplitude()
event_data = amplitude.build_event_data(
    event_type='Some event type',
    request=request,
    app_version='1.0.0',
)
amplitude.send_events([event_data])
```


### Building you own event

If you are not happy with the data from `build_event_data` you can build you own event data based on the `UploadRequestBody` type in [Amplitude HTTP API (v2)](https://developers.amplitude.com/docs/http-api-v2). If you want to do this There are a few helper functions to build different parts of the event data from the Django request object:

```python
amplitude.event_properties_from_request(request)
amplitude.device_data_from_request(request)
amplitude.user_properties_from_request(request)
amplitude.group_from_request(request)

amplitude.location_data_from_ip_address(ip_address)
```

* `user_properties_from_request` will return an empty dict if `AMPLITUDE_INCLUDE_USER_DATA` is `False`
* `group_from_request` will return an empty dict if `AMPLITUDE_INCLUDE_GROUP_DATA` is `False`
