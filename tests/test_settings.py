from importlib import reload

import pytest
from django.core.exceptions import ImproperlyConfigured


def test_missing_api_key(settings):
    settings.AMPLITUDE_API_KEY = None

    with pytest.raises(ImproperlyConfigured):
        from amplitude import settings
        reload(settings)
