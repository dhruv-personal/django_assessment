"""
Main package initialization for Events Platform.
"""

from events_platform.celery import app as celery_app

__all__ = ("celery_app",)
