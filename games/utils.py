"""
Utility functions and custom exception handler for the Steam Games API.
"""

from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def custom_exception_handler(exc, context):
    """
    Custom DRF exception handler that wraps all error responses in a
    consistent envelope:

        {
            "success": false,
            "error": {
                "code": <HTTP status code>,
                "message": "<human-readable summary>",
                "details": <original DRF error detail>
            }
        }

    Falls back to DRF's default handler for unrecognised exceptions.
    """
    response = exception_handler(exc, context)

    if response is not None:
        error_detail = response.data

        # Flatten single-key detail dicts for cleaner messages
        if isinstance(error_detail, dict) and 'detail' in error_detail:
            message = str(error_detail['detail'])
        elif isinstance(error_detail, list) and len(error_detail) == 1:
            message = str(error_detail[0])
        else:
            message = _status_message(response.status_code)

        response.data = {
            "success": False,
            "error": {
                "code": response.status_code,
                "message": message,
                "details": error_detail,
            }
        }

    return response


def _status_message(status_code: int) -> str:
    """Return a human-readable summary for common HTTP status codes."""
    messages = {
        400: "Bad request. Please check your input.",
        401: "Authentication credentials were not provided or are invalid.",
        403: "You do not have permission to perform this action.",
        404: "The requested resource was not found.",
        405: "HTTP method not allowed.",
        409: "Conflict: the resource already exists.",
        422: "Unprocessable entity. Validation failed.",
        429: "Too many requests. Please slow down.",
        500: "Internal server error. Please try again later.",
    }
    return messages.get(status_code, "An unexpected error occurred.")


def paginated_response(data, message: str = "OK", extra: dict = None) -> dict:
    """
    Wraps a paginated DRF response in a standard success envelope.
    Used by analytics views that return non-paginated results.
    """
    payload = {
        "success": True,
        "message": message,
        "data": data,
    }
    if extra:
        payload.update(extra)
    return payload
