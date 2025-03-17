class AuthenticationError(Exception):
    """Raised when a request fails due to invalid authentication."""

class RequestError(Exception):
    """Raised when a request to the Ed server fails."""