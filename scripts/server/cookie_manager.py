"""
HttpOnly cookie utilities for secure token storage.
Refresh tokens stored in secure HttpOnly cookies are protected against XSS attacks.
"""
from datetime import datetime, timedelta, timezone
from fastapi import Response
from typing import Optional


class HttpOnlyCookieManager:
    """Manages secure HttpOnly cookies for token storage."""

    # Cookie names
    REFRESH_TOKEN_COOKIE = "refresh_token"
    CSRF_TOKEN_COOKIE = "X-CSRF-Token"

    @staticmethod
    def set_refresh_token_cookie(
        response: Response,
        token: str,
        expires_at: datetime,
        secure: bool = True,
        domain: Optional[str] = None,
    ) -> None:
        """
        Set refresh token in HttpOnly, Secure, SameSite cookie.

        Args:
            response: FastAPI Response object
            token: Refresh token to store
            expires_at: Token expiration datetime
            secure: Only send over HTTPS (default True for production)
            domain: Cookie domain (optional)
        """
        # Calculate max_age
        now = datetime.now(timezone.utc)
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        max_age = max(0, int((expires_at - now).total_seconds()))

        response.set_cookie(
            key=HttpOnlyCookieManager.REFRESH_TOKEN_COOKIE,
            value=token,
            max_age=max_age,
            expires=expires_at.isoformat(),
            httponly=True,  # JavaScript cannot access this cookie
            secure=secure,  # Only send over HTTPS
            samesite="strict",  # CSRF protection - Strict is most secure
            domain=domain,
        )

    @staticmethod
    def set_csrf_token_cookie(
        response: Response,
        token: str,
        max_age: int = 3600,
        secure: bool = True,
        domain: Optional[str] = None,
    ) -> None:
        """
        Set CSRF token in readable cookie (needed for double-submit pattern).

        Args:
            response: FastAPI Response object
            token: CSRF token
            max_age: Cookie age in seconds (default 1 hour)
            secure: Only send over HTTPS (default True for production)
            domain: Cookie domain (optional)
        """
        response.set_cookie(
            key=HttpOnlyCookieManager.CSRF_TOKEN_COOKIE,
            value=token,
            max_age=max_age,
            httponly=False,  # JavaScript needs to read this for CSRF header
            secure=secure,
            samesite="strict",
            domain=domain,
        )

    @staticmethod
    def clear_refresh_token_cookie(response: Response) -> None:
        """Clear refresh token cookie (on logout)."""
        response.delete_cookie(
            key=HttpOnlyCookieManager.REFRESH_TOKEN_COOKIE,
            httponly=True,
            secure=True,
            samesite="strict",
        )

    @staticmethod
    def clear_csrf_token_cookie(response: Response) -> None:
        """Clear CSRF token cookie."""
        response.delete_cookie(
            key=HttpOnlyCookieManager.CSRF_TOKEN_COOKIE,
            secure=True,
            samesite="strict",
        )

    @staticmethod
    def get_refresh_token_from_cookie(request) -> Optional[str]:
        """Extract refresh token from request cookies."""
        return request.cookies.get(HttpOnlyCookieManager.REFRESH_TOKEN_COOKIE)
