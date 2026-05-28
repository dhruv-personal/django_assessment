"""
Utility functions for authentication.
"""

import logging
import random
import string

from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

from authentication.models import OTP
from events_platform.constants import (
    OTP_EMAIL_BODY,
    OTP_EMAIL_SUBJECT,
    OTP_EXPIRY_MINUTES,
    OTP_LENGTH,
    OTP_MAX_ATTEMPTS,
)

logger = logging.getLogger(__name__)


def generate_otp():
    """
    Generate a random 6-digit OTP code.
    """
    return "".join(random.choices(string.digits, k=OTP_LENGTH))


def send_otp_email(user, otp_code):
    """
    Send OTP verification email to user.
    """
    subject = OTP_EMAIL_SUBJECT
    message = OTP_EMAIL_BODY.format(otp_code=otp_code, expiry_minutes=OTP_EXPIRY_MINUTES)

    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        logger.info(f"OTP email sent to {user.email}")
    except Exception as e:
        logger.error(f"Failed to send OTP email to {user.email}: {str(e)}")
        raise


def create_and_send_otp(user):
    """
    Create a new OTP for user and send via email.
    """
    OTP.objects.filter(user=user, is_used=False).delete()

    otp_code = generate_otp()
    otp = OTP.objects.create(
        user=user,
        code=otp_code,
        expires_at=timezone.now() + timezone.timedelta(minutes=OTP_EXPIRY_MINUTES),
    )

    send_otp_email(user, otp_code)

    return otp


def validate_otp(user, code):
    """
    Validate OTP code for user.
    Returns tuple (is_valid, message).
    """
    try:
        otp = OTP.objects.filter(user=user, is_used=False).order_by("-created_at").first()

        if not otp:
            return False, "No OTP found for this user"

        if otp.attempts >= OTP_MAX_ATTEMPTS:
            return False, "Maximum OTP attempts exceeded"

        if timezone.now() > otp.expires_at:
            return False, "OTP has expired"

        otp.attempts += 1
        otp.save()

        if otp.code != code:
            return False, "Invalid OTP"

        otp.is_used = True
        otp.save()

        return True, "OTP verified successfully"

    except Exception as e:
        logger.error(f"Error validating OTP for {user.email}: {str(e)}")
        return False, str(e)
