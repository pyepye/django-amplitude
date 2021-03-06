import os

SECRET_KEY = 'amplitude-test'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'
SESSION_COOKIE_HTTPONLY = True
SESSION_SAVE_EVERY_REQUEST = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

ROOT_URLCONF = 'tests.urls'
INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'amplitude',
    'tests',
]

MIDDLEWARE = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'amplitude.middleware.SessionInfo',
    'amplitude.middleware.SendPageViewEvent',
]

AMPLITUDE_API_KEY = 'abc123'
AMPLITUDE_INCLUDE_USER_DATA = True
AMPLITUDE_INCLUDE_GROUP_DATA = True
