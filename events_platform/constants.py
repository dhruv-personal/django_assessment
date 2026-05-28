"""
Global constants for the Events Platform application.
"""

OTP_EXPIRY_MINUTES = 5
OTP_MAX_ATTEMPTS = 3
OTP_LENGTH = 6

JWT_ACCESS_TOKEN_LIFETIME_MINUTES = 15
JWT_REFRESH_TOKEN_LIFETIME_DAYS = 7

PAGINATION_PAGE_SIZE = 25

FOLLOWUP_EMAIL_DELAY_SECONDS = 3600  # 1 hour
REMINDER_EMAIL_WINDOW_MINUTES = (55, 65)  # 55 to 65 minutes before event

OTP_EMAIL_SUBJECT = "Email Verification - Events Platform"
OTP_EMAIL_BODY = """
Hello,

Your OTP for email verification is: {otp_code}

This OTP will expire in {expiry_minutes} minutes.

If you didn't request this, please ignore this email.

Best regards,
Events Platform Team
"""

FOLLOWUP_EMAIL_SUBJECT = "Thank you for enrolling in {event_title}"
FOLLOWUP_EMAIL_BODY = """
Hello,

Thank you for enrolling in "{event_title}".

Event Details:
- Title: {event_title}
- Location: {event_location}
- Start Time: {starts_at}
- End Time: {ends_at}

We look forward to seeing you there!

Best regards,
Events Platform Team
"""

REMINDER_EMAIL_SUBJECT = "Reminder: {event_title} starts in 1 hour"
REMINDER_EMAIL_BODY = """
Hello,

This is a reminder that the event "{event_title}" you enrolled in will start in approximately 1 hour.

Event Details:
- Title: {event_title}
- Location: {event_location}
- Start Time: {starts_at}
- End Time: {ends_at}

See you soon!

Best regards,
Events Platform Team
"""

USER_ROLE_SEEKER = "SEEKER"
USER_ROLE_FACILITATOR = "FACILITATOR"

ENROLLMENT_STATUS_ENROLLED = "ENROLLED"
ENROLLMENT_STATUS_CANCELED = "CANCELED"

ERROR_CODE_VALIDATION = "validation_error"
ERROR_CODE_AUTHENTICATION_FAILED = "authentication_failed"
ERROR_CODE_PERMISSION_DENIED = "permission_denied"
ERROR_CODE_NOT_FOUND = "not_found"
ERROR_CODE_OTP_EXPIRED = "otp_expired"
ERROR_CODE_OTP_INVALID = "otp_invalid"
ERROR_CODE_OTP_MAX_ATTEMPTS = "otp_max_attempts"
ERROR_CODE_EMAIL_NOT_VERIFIED = "email_not_verified"
ERROR_CODE_INVALID_CREDENTIALS = "invalid_credentials"
ERROR_CODE_USER_NOT_FOUND = "user_not_found"
ERROR_CODE_ALREADY_ENROLLED = "already_enrolled"
ERROR_CODE_EVENT_FULL = "event_full"
ERROR_CODE_PAST_EVENT = "past_event"
