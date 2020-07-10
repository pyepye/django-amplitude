# Django Amplitude

Integration between Django and [Amplitude.com](https://amplitude.com/) to help send events via the [Amplitude HTTP API (v2)](https://developers.amplitude.com/docs/http-api-v2)


## Quick start

### Installation

```bash
pip install django-amplitude
```

Set a Amplitude API key in your Django settings:
```python
# Settings > Projects > <Your project> > General > API Key
AMPLITUDE_API_KEY = '<amplitude-project-api-key>'

# You can also choose if you want to include user and group data
# IF not set will default to False
AMPLITUDE_INCLUDE_USER_DATA = True
AMPLITUDE_INCLUDE_GROUP_DATA = True
```

Add `amplitude` to your `INSTALLED_APPS`:

```python
INSTALLED_APPS =(
    ...
    "amplitude",
    ...
)
```


## Usage

If you want to send an event to Amplitude on every page view you can use the django-amplitude `SendPageViewEvent` middleware to your `MIDDLEWARE` in your Django settings.
This will automatically create an event base on the url name that was hit and the Django request object.

```python
MIDDLEWARE = [
    ...
    'amplitude.middleware.SendPageViewEvent',
    ...
]
```

If you want to send your own events:
```python
from amplitude import Amplitude

amplitude = Amplitude()
amplitude.send_events([event_data])  # https://developers.amplitude.com/docs/http-api-v2
```

There are also few helper functions to build different parts of the event data:
```python
amplitude.session_id_from_request(request)
amplitude.event_properties_from_request(request)
amplitude.device_data_from_request(request)
amplitude.user_properties_from_request(request)
amplitude.group_from_request(request)

amplitude.location_data_from_ip_address(ip_address)
```

* `user_properties_from_request` will return an empty dict is `AMPLITUDE_INCLUDE_USER_DATA` is `False`
* `group_from_request` will return an empty dict is `AMPLITUDE_INCLUDE_GROUP_DATA` is `False`



### SendPageViewEvent - missing event data keys

The `SendPageViewEvent` middleware currently does not record the following keys from `UploadRequestBody`:

* event_id
* app_version
* device_id
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

If you want to record an event in Amplitude with any of these keys you must use `amplitude.send_events([event_data])`
