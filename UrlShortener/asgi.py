"""
ASGI config for UrlShortener project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/asgi/
"""

import os
from decouple import config

from django.core.asgi import get_asgi_application

if config('DJANGO_DEVELOPMENT') == 'dev':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'UrlShortener.settings.development')
elif config('DJANGO_DEVELOPMENT') == 'production':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'UrlShortener.settings.settings')
else:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'UrlShortener.settings.settings')

application = get_asgi_application()
