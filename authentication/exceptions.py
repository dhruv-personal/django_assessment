from rest_framework.exceptions import (
    AuthenticationFailed,
    NotFound,
    PermissionDenied,
    ValidationError,
)
from rest_framework.response import Response
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        custom_response_data = {"detail": response.data.get("detail", str(exc)), "code": get_error_code(exc)}

        if isinstance(response.data, dict):
            if "detail" not in response.data and len(response.data) > 0:
                first_key = list(response.data.keys())[0]
                first_error = response.data[first_key]
                if isinstance(first_error, list):
                    custom_response_data["detail"] = first_error[0]
                else:
                    custom_response_data["detail"] = first_error

        response.data = custom_response_data

    return response


def get_error_code(exc):
    error_code_map = {
        ValidationError: "validation_error",
        AuthenticationFailed: "authentication_failed",
        PermissionDenied: "permission_denied",
        NotFound: "not_found",
    }

    for exc_class, code in error_code_map.items():
        if isinstance(exc, exc_class):
            return code

    return "error"
