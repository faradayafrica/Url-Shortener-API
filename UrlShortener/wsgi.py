"""
WSGI config for UrlShortener project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application
from whitenoise import WhiteNoise

if os.environ.get('DJANGO_DEVELOPMENT', 'true'):
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'UrlShortener.settings.development')
else:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'UrlShortener.settings.production')

application = get_wsgi_application()
application = WhiteNoise(application)