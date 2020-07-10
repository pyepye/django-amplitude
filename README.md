# Django Amplitude

Intergration between Django and [Amplitude.com](https://amplitude.com/)

## Quick start

### Installation

```bash
pip install django-amplitude
```


Add `amplitude` to your Django settings:

```python
INSTALLED_APPS =(
    ...
    "amplitude",
    ...
)
```


### Usage

If you want to send an event to Amplitude on every page view you can use the django-amplitude SendPageViewEvent middleware. This will created an event base on the url name that was hit and the Django request object

```python
MIDDLEWARE = [
    ...
    'amplitude.middleware.SendPageViewEvent',
]
```

If you want to send your own events:
```python
from amplitude import Amplitude

amplitude = Amplitude()
amplitude.send_events([event_data])  # https://developers.amplitude.com/docs/http-api-v2
```
