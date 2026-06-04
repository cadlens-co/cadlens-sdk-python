class CadlensError(Exception):
    """Base exception for all Cadlens SDK errors."""

    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


class AuthError(CadlensError):
    """Raised when the API key is invalid or missing."""


class JobNotReadyError(CadlensError):
    """Raised when fetching a result for a job that is not yet COMPLETED."""


class JobFailedError(CadlensError):
    """Raised when a job transitions to FAILED status."""


class TimeoutError(CadlensError):
    """Raised when parseAndWait exceeds the configured timeout."""
