"""
Custom exception handler for the Events Platform application.
"""

import logging

from rest_framework import status
from rest_framework.exceptions import (
    AuthenticationFailed,
    NotFound,
    PermissionDenied,
    ValidationError,
)
from rest_framework.response import Response
from rest_framework.views import exception_handler

from events_platform.constants import (
    ERROR_CODE_AUTHENTICATION_FAILED,
    ERROR_CODE_NOT_FOUND,
    ERROR_CODE_PERMISSION_DENIED,
    ERROR_CODE_VALIDATION,
)

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Custom exception handler that ensures consistent error response format.
    """
    response = exception_handler(exc, context)

    if response is not None:
        error_code = get_error_code(exc)

        custom_response_data = {
            "detail": get_error_detail(response.data, exc),
            "code": error_code,
        }

        logger.error(f"Exception occurred: {exc.__class__.__name__} - {str(exc)}", exc_info=True)

        response.data = custom_response_data

    return response


def get_error_code(exc):
    """
    Map exception types to standardized error codes.
    """
    error_code_map = {
        ValidationError: ERROR_CODE_VALIDATION,
        AuthenticationFailed: ERROR_CODE_AUTHENTICATION_FAILED,
        PermissionDenied: ERROR_CODE_PERMISSION_DENIED,
        NotFound: ERROR_CODE_NOT_FOUND,
    }

    for exc_class, code in error_code_map.items():
        if isinstance(exc, exc_class):
            return code

    return "error"


def get_error_detail(response_data, exc):
    """
    Extract error detail message from response data.
    """
    if isinstance(response_data, dict):
        if "detail" in response_data:
            return response_data["detail"]

        if len(response_data) > 0:
            first_key = list(response_data.keys())[0]
            first_error = response_data[first_key]

            if isinstance(first_error, list):
                return first_error[0]
            return first_error

    return str(exc)
