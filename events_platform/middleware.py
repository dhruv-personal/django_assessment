"""
Custom middleware for the Events Platform application.
"""

import json
import logging

from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)


class ResponseFormatterMiddleware(MiddlewareMixin):
    """
    Middleware to ensure consistent response format across the application.
    Formats all API responses to include standard fields.
    """

    def process_response(self, request, response):
        if not request.path.startswith("/api/") and not request.path.startswith("/auth/"):
            return response

        if isinstance(response, JsonResponse):
            return response

        if hasattr(response, "data") and isinstance(response.data, dict):
            return response

        return response
