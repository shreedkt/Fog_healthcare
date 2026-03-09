"""
String constants shared across the platform.

Using constants instead of magic strings improves maintainability
and makes typos a visible ``AttributeError`` instead of a silent bug.
"""


class AuditAction:
    """Action types recorded in the audit log."""

    READ: str = "READ"
    CREATE: str = "CREATE"
    UPDATE: str = "UPDATE"
    DELETE: str = "DELETE"
    FORWARD: str = "FORWARD"


class ErrorMessages:
    """Standard error messages returned by the API."""

    INVALID_CREDENTIALS: str = "Invalid username or password."
    SESSION_EXPIRED: str = "Session has expired. Please log in again."
    INTEGRITY_FAILED: str = "Data integrity verification failed."
    RECORD_NOT_FOUND: str = "Requested medical record does not exist."
    PERMISSION_DENIED: str = "You do not have permission to perform this action."
    CLOUD_UNAVAILABLE: str = "Cloud service is temporarily unavailable."
    ENCRYPTION_FAILED: str = "Encryption operation failed."
    DECRYPTION_FAILED: str = "Decryption operation failed."


class SuccessMessages:
    """Standard success messages returned by the API."""

    LOGIN_SUCCESS: str = "Login successful."
    LOGOUT_SUCCESS: str = "Logout successful."
    RECORD_CREATED: str = "Medical record created successfully."
    RECORD_UPDATED: str = "Medical record updated successfully."
    RECORD_DELETED: str = "Medical record deleted successfully."
    CLOUD_FORWARDED: str = "Data forwarded to cloud successfully."
