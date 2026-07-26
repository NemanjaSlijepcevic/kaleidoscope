"""
WSGI config for kaleidoscope project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kaleidoscope.settings')

application = get_wsgi_application()

from django.conf import settings  # noqa: E402  (must follow get_wsgi_application)
from whitenoise import WhiteNoise  # noqa: E402

if not settings.DEBUG:
    cache_root = settings.MEDIA_ROOT / 'CACHE'
    cache_root.mkdir(parents=True, exist_ok=True)
    application = WhiteNoise(application, autorefresh=True, max_age=86400)
    application.add_files(cache_root, prefix='media/CACHE/')
