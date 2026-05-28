"""
Signal handlers for authentication models.
"""

import logging

from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from authentication.models import UserProfile
from events_platform.constants import USER_ROLE_SEEKER

logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Create user profile automatically when a new user is created.
    """
    if created and not hasattr(instance, "profile"):
        role = getattr(instance, "_profile_role", USER_ROLE_SEEKER)
        UserProfile.objects.create(user=instance, role=role)
        logger.info(f"User profile created for {instance.email} with role {role}")


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Save user profile when user is saved.
    """
    if hasattr(instance, "profile"):
        instance.profile.save()
