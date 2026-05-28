"""
Celery configuration for the Events Platform.
"""

import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "events_platform.settings")

app = Celery("events_platform")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """
    Debug task for testing Celery setup.
    """
    print(f"Request: {self.request!r}")
