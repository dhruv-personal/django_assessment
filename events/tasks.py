"""
Celery tasks for events app.
"""

import logging
from datetime import timedelta

from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

from celery import shared_task

from events.models import Enrollment, Event
from events_platform.constants import (
    ENROLLMENT_STATUS_ENROLLED,
    FOLLOWUP_EMAIL_BODY,
    FOLLOWUP_EMAIL_SUBJECT,
    REMINDER_EMAIL_BODY,
    REMINDER_EMAIL_SUBJECT,
    REMINDER_EMAIL_WINDOW_MINUTES,
)

logger = logging.getLogger(__name__)


@shared_task
def send_followup_email(enrollment_id):
    """
    Send follow-up email to seeker 1 hour after enrollment.
    """
    try:
        enrollment = Enrollment.objects.get(id=enrollment_id)

        if enrollment.status != ENROLLMENT_STATUS_ENROLLED:
            logger.info(f"Enrollment {enrollment_id} is not active, skipping follow-up email")
            return f"Enrollment {enrollment_id} is not active"

        event = enrollment.event
        subject = FOLLOWUP_EMAIL_SUBJECT.format(event_title=event.title)
        message = FOLLOWUP_EMAIL_BODY.format(
            event_title=event.title,
            event_location=event.location,
            starts_at=event.starts_at.strftime("%Y-%m-%d %H:%M UTC"),
            ends_at=event.ends_at.strftime("%Y-%m-%d %H:%M UTC"),
        )

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [enrollment.seeker.email],
            fail_silently=False,
        )

        logger.info(f"Follow-up email sent to {enrollment.seeker.email} for event {event.title}")
        return f"Follow-up email sent to {enrollment.seeker.email}"

    except Enrollment.DoesNotExist:
        logger.error(f"Enrollment {enrollment_id} not found")
        return f"Enrollment {enrollment_id} not found"
    except Exception as e:
        logger.error(f"Error sending follow-up email for enrollment {enrollment_id}: {str(e)}")
        return f"Error sending follow-up email: {str(e)}"


@shared_task
def send_reminder_emails():
    """
    Send reminder emails to seekers 1 hour before event starts.
    Runs periodically every 10 minutes.
    """
    now = timezone.now()
    min_window, max_window = REMINDER_EMAIL_WINDOW_MINUTES
    start_time = now + timedelta(minutes=min_window)
    end_time = now + timedelta(minutes=max_window)

    upcoming_events = Event.objects.filter(starts_at__gte=start_time, starts_at__lte=end_time)

    emails_sent = 0

    for event in upcoming_events:
        enrollments = Enrollment.objects.filter(event=event, status=ENROLLMENT_STATUS_ENROLLED, reminder_sent=False)

        for enrollment in enrollments:
            try:
                subject = REMINDER_EMAIL_SUBJECT.format(event_title=event.title)
                message = REMINDER_EMAIL_BODY.format(
                    event_title=event.title,
                    event_location=event.location,
                    starts_at=event.starts_at.strftime("%Y-%m-%d %H:%M UTC"),
                    ends_at=event.ends_at.strftime("%Y-%m-%d %H:%M UTC"),
                )

                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [enrollment.seeker.email],
                    fail_silently=False,
                )

                enrollment.reminder_sent = True
                enrollment.save()

                emails_sent += 1
                logger.info(f"Reminder email sent to {enrollment.seeker.email} for event {event.title}")

            except Exception as e:
                logger.error(f"Error sending reminder to {enrollment.seeker.email} for event {event.title}: {str(e)}")
                continue

    logger.info(f"Sent {emails_sent} reminder emails")
    return f"Sent {emails_sent} reminder emails"
