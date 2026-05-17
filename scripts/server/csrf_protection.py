"""
CSRF (Cross-Site Request Forgery) protection middleware and utilities.
Implements double-submit cookie pattern for CSRF protection.
"""
import secrets
import hashlib
from typing import Optional
from fastapi import Request, HTTPException, status


def generate_csrf_token() -> str:
    """Generate a cryptographically secure CSRF token."""
    return secrets.token_urlsafe(32)


def hash_csrf_token(token: str) -> str:
    """Hash CSRF token for storage in cookie."""
    return hashlib.sha256(token.encode()).hexdigest()


class CSRFProtection:
    """CSRF protection using double-submit cookie pattern."""

    CSRF_COOKIE_NAME = "X-CSRF-Token"
    CSRF_HEADER_NAME = "X-CSRF-Token"
    SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}

    @staticmethod
    def is_safe_method(method: str) -> bool:
        """Check if HTTP method is safe (doesn't modify state)."""
        return method in CSRFProtection.SAFE_METHODS

    @staticmethod
    async def verify_csrf_token(request: Request) -> bool:
        """
        Verify CSRF token from request.
        
        Implements double-submit cookie pattern:
        1. Check if cookie-based CSRF token exists
        2. Verify header token matches cookie token
        
        Args:
            request: FastAPI request object
            
        Returns:
            True if CSRF token valid, raises HTTPException if invalid
        """
        # Skip verification for safe methods
        if CSRFProtection.is_safe_method(request.method):
            return True

        # Get token from cookie
        cookie_token = request.cookies.get(CSRFProtection.CSRF_COOKIE_NAME)
        if not cookie_token:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="CSRF token missing from cookie",
            )

        # Get token from header or form body
        header_token = request.headers.get(CSRFProtection.CSRF_HEADER_NAME)
        if not header_token:
            # Try to get from form body (for backward compatibility)
            try:
                body = await request.json()
                header_token = body.get("csrf_token")
            except Exception:
                pass

        if not header_token:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="CSRF token missing from request",
            )

        # Verify tokens match
        if not _constant_time_compare(cookie_token, header_token):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="CSRF token validation failed",
            )

        return True


def _constant_time_compare(a: str, b: str) -> bool:
    """
    Compare two strings in constant time to prevent timing attacks.
    """
    if len(a) != len(b):
        return False

    result = 0
    for x, y in zip(a.encode(), b.encode()):
        result |= x ^ y

    return result == 0
