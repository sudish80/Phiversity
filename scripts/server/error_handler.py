"""
Standardized API error response handling.
Provides consistent error format across all endpoints.
"""
from typing import Optional, Any, Dict
from pydantic import BaseModel
from datetime import datetime, timezone


class ErrorDetail(BaseModel):
    """Standard error response format"""
    timestamp: str
    status_code: int
    error_type: str  # e.g., "validation_error", "authentication_error", "not_found", "server_error"
    message: str  # Human-readable error message
    request_id: Optional[str] = None  # For tracing
    details: Optional[Dict[str, Any]] = None  # Additional context


class ValidationErrorDetail(ErrorDetail):
    """Validation error response"""
    errors: Optional[list[Dict[str, str]]] = None  # List of validation failures


def create_error_response(
    status_code: int,
    error_type: str,
    message: str,
    request_id: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Create standardized error response.
    
    Args:
        status_code: HTTP status code
        error_type: Type of error (validation_error, authentication_error, etc.)
        message: Human-readable error message  
        request_id: Optional request tracing ID
        details: Optional context-specific details
        
    Returns:
        Dict with standardized error format suitable for HTTPException detail
    """
    return {
        "error": {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status_code": status_code,
            "error_type": error_type,
            "message": message,
            "request_id": request_id,
            "details": details,
        }
    }


# Error type constants
ERROR_TYPES = {
    "validation_error": "Input validation failed",
    "authentication_error": "Authentication failed",
    "authorization_error": "Insufficient permissions",
    "not_found_error": "Resource not found",
    "conflict_error": "Resource conflict",
    "rate_limit_error": "Rate limit exceeded",
    "server_error": "Internal server error",
    "external_service_error": "External service unavailable",
    "bad_request": "Bad request",
    "account_locked": "Account temporarily locked",
}


# Common error messages
ERRORS = {
    # Auth errors
    "INVALID_CREDENTIALS": ("Invalid email or password", "authentication_error"),
    "ACCOUNT_LOCKED": ("Account temporarily locked due to too many failed attempts", "account_locked"),
    "INVALID_TOKEN": ("Invalid or expired token", "authentication_error"),
    "INSUFFICIENT_PERMISSIONS": ("Insufficient permissions for this operation", "authorization_error"),
    "SESSION_EXPIRED": ("Your session has expired. Please log in again", "authentication_error"),
    
    # Validation errors
    "EMAIL_REQUIRED": ("Email is required", "validation_error"),
    "PASSWORD_REQUIRED": ("Password is required", "validation_error"),
    "WEAK_PASSWORD": ("Password does not meet strength requirements", "validation_error"),
    "EMAIL_ALREADY_REGISTERED": ("Email already registered", "conflict_error"),
    "INVALID_EMAIL_FORMAT": ("Invalid email format", "validation_error"),
    
    # Not found errors
    "USER_NOT_FOUND": ("User not found", "not_found_error"),
    "RESOURCE_NOT_FOUND": ("Resource not found", "not_found_error"),
    
    # Rate limiting
    "RATE_LIMIT_EXCEEDED": ("Rate limit exceeded. Please try again later", "rate_limit_error"),
    "TOO_MANY_REQUESTS": ("Too many requests. Please try again later", "rate_limit_error"),
    
    # Server errors
    "INTERNAL_ERROR": ("An unexpected error occurred. Please try again later", "server_error"),
    "SERVICE_UNAVAILABLE": ("Service temporarily unavailable", "server_error"),
}


def get_error_details(error_key: str, details: Optional[Dict[str, Any]] = None) -> tuple[str, str]:
    """
    Get standardized error message and type.
    
    Args:
        error_key: Key from ERRORS dict
        details: Additional context details
        
    Returns:
        Tuple of (message, error_type)
    """
    if error_key in ERRORS:
        return ERRORS[error_key]
    return ("An error occurred", "server_error")
