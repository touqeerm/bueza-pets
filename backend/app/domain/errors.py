class InvalidOtpError(Exception):
    """Raised when an OTP code is missing, expired, or does not match."""


class InvalidSessionError(Exception):
    """Raised when a session token is missing, expired, or unknown."""
