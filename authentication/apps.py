"""
App configuration for authentication.
"""

from django.apps import AppConfig


class AuthenticationConfig(AppConfig):
    """
    Configuration for the authentication application.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "authentication"

    def ready(self):
        """
        Import signals when the app is ready.
        """
        import authentication.signals  # noqa
