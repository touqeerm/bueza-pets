class InvalidOtpError(Exception):
    """Raised when an OTP code is missing, expired, or does not match."""


class InvalidSessionError(Exception):
    """Raised when a session token is missing, expired, or unknown."""


class InvalidExperimentTransitionError(Exception):
    """Raised when an experiment status transition or edit isn't allowed from its current status."""


class ExperimentNotEvaluableError(Exception):
    """Raised when an experiment is started or evaluated without any metrics configured."""


class AdminAccessRequiredError(Exception):
    """Raised when a non-admin user calls an admin-only endpoint."""
