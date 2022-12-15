import enum


class StatusCode(enum.Enum):
    """Represents HTTP Status Codes used in application."""

    NOT_FOUND = 404
    FORBIDDEN = 403


class HTTPMethod(enum.Enum):
    """Represents HTTP methods used in applciation."""

    GET = "GET"
    POST = "POST"
