import os
from pathlib import Path
from django.core.management.utils import get_random_secret_key

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', get_random_secret_key())

DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1', '0.0.0.0']

BASE_DIR = Path(__file__).resolve().parent.parent

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

SECURE_SSL_REDIRECT = False