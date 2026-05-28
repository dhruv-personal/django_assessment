"""
WSGI config for events_platform project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "events_platform.settings")

application = get_wsgi_application()
