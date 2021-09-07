from django import get_version
from packaging import version

from .amplitude import Amplitude  # NOQA: F401

"""
To stop waring:
    RemovedInDjango41Warning: 'amplitude' defines
    default_app_config = 'amplitude.apps.AmplitudeConfig'. Django now detects
    this configuration automatically. You can remove default_app_config.
"""
if version.parse(get_version()) < version.parse('3.2'):  # pragma: no cover
    default_app_config = "amplitude.apps.AmplitudeConfig"
