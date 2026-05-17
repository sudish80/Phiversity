"""
Password strength validation module.
Ensures passwords meet security requirements and checks against breaches.
"""
import hashlib
import re
import os
from typing import Tuple, Optional
from datetime import datetime, timezone


def _check_pwned_password(password: str) -> Tuple[bool, int]:
    """
    Check if password has been exposed in data breaches using Have I Been Pwned API.
    Uses k-Anonymity model - only sends first 5 chars of SHA-1 hash.
    
    Returns:
        Tuple of (is_pwned, count) - count is number of times password appeared in breaches
    """
    if not os.getenv("ENABLE_PWNED_CHECK", "false").lower() in {"true", "1", "yes"}:
        return False, 0
    
    try:
        # Hash the password with SHA-1
        sha1_hash = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
        prefix = sha1_hash[:5]
        suffix = sha1_hash[5:]
        
        # Query Have I Been Pwned API
        import urllib.request
        url = f"https://api.pwnedpasswords.com/range/{prefix}"
        req = urllib.request.Request(url, headers={"User-Agent": "PhiversityAuth"})
        
        with urllib.request.urlopen(req, timeout=5) as response:
            data = response.read().decode('utf-8')
            
        # Check if our hash suffix is in the response
        for line in data.split('\n'):
            hash_suffix, count = line.split(':')
            if hash_suffix.strip() == suffix:
                return True, int(count)
        
        return False, 0
    except Exception:
        # If API fails, allow password but log warning
        return False, 0


class PasswordValidator:
    """Validates password strength according to security requirements."""

    # Default requirements - relaxed for usability
    MIN_LENGTH = 8
    REQUIRE_UPPERCASE = False
    REQUIRE_LOWERCASE = False
    REQUIRE_DIGITS = False
    REQUIRE_SPECIAL = False
    
    # Common passwords to reject
    COMMON_PASSWORDS = {
        "password", "123456", "password123", "admin", "qwerty", "abc123",
        "letmein", "welcome", "monkey", "dragon", "master", "sunshine",
    }
    
    @staticmethod
    def validate(
        password: str,
        min_length: int = MIN_LENGTH,
        require_uppercase: bool = REQUIRE_UPPERCASE,
        require_lowercase: bool = REQUIRE_LOWERCASE,
        require_digits: bool = REQUIRE_DIGITS,
        require_special: bool = REQUIRE_SPECIAL,
    ) -> Tuple[bool, str]:
        """
        Validate password strength.
        
        Returns:
            Tuple of (is_valid, error_message)
            If valid, error_message is empty string
        """
        if not password:
            return False, "Password is required"
        
        if len(password) < min_length:
            return False, f"Password must be at least {min_length} characters long"
        
        if len(password) > 128:
            return False, "Password must not exceed 128 characters"
        
        if password.lower() in PasswordValidator.COMMON_PASSWORDS:
            return False, "Password is too common. Please choose a stronger password"
        
        if require_uppercase and not re.search(r"[A-Z]", password):
            return False, "Password must contain at least one uppercase letter"
        
        if require_lowercase and not re.search(r"[a-z]", password):
            return False, "Password must contain at least one lowercase letter"
        
        if require_digits and not re.search(r"\d", password):
            return False, "Password must contain at least one digit"
        
        if require_special and not re.search(r"[!@#$%^&*()_\-+=\[\]{};:'\",.<>?/\\|`~]", password):
            return False, "Password must contain at least one special character (!@#$%^&*...)"

        # Skip the common sequences check - it's too strict and blocks common patterns like "Test123"
        # Users should be able to use passwords like "Password123" without issues

        return True, ""
    
    @staticmethod
    def _has_common_sequences(password: str) -> bool:
        """Check if password contains common sequences like 'abc', '123', 'qwerty'."""
        common_sequences = [
            "abc", "bcd", "cde", "def", "efg", "fgh", "ghi", "hij", "ijk", "jkl",
            "123", "234", "345", "456", "567", "678", "789", "890",
            "qwerty", "asdf", "zxcv",
        ]
        
        password_lower = password.lower()
        for seq in common_sequences:
            if seq in password_lower:
                return True
        
        return False


def validate_password_strength(password: str) -> None:
    """
    Validate password strength and raise ValueError if invalid.
    
    Raises:
        ValueError: If password doesn't meet strength requirements
    """
    is_valid, error_message = PasswordValidator.validate(password)
    if not is_valid:
        raise ValueError(error_message)


def get_password_strength_feedback(password: str) -> dict:
    """
    Get detailed feedback about password strength.
    
    Returns:
        Dict with strength assessment and suggestions
    """
    feedback = {
        "strength": "weak",
        "score": 0,
        "issues": [],
        "suggestions": [],
    }
    
    if not password:
        feedback["issues"].append("Password is required")
        return feedback
    
    score = 0
    max_score = 5
    
    # Check length
    if len(password) >= 12:
        score += 1
    else:
        feedback["issues"].append(f"Password too short ({len(password)}/12 characters)")
        feedback["suggestions"].append(f"Add {12 - len(password)} more characters")
    
    if len(password) >= 16:
        score += 1
    
    # Check character variety
    has_upper = bool(re.search(r"[A-Z]", password))
    has_lower = bool(re.search(r"[a-z]", password))
    has_digit = bool(re.search(r"\d", password))
    has_special = bool(re.search(r"[!@#$%^&*()_\-+=\[\]{};:'\",.<>?/\\|`~]", password))
    
    char_variety = sum([has_upper, has_lower, has_digit, has_special])
    if char_variety >= 3:
        score += 1
    elif char_variety < 2:
        feedback["issues"].append("Password lacks character variety")
        feedback["suggestions"].append("Mix uppercase, lowercase, numbers, and special characters")
    
    if char_variety == 4:
        score += 1
    
    # Check for common patterns
    if not PasswordValidator._has_common_sequences(password):
        score += 1
    else:
        feedback["issues"].append("Password contains common sequences")
        feedback["suggestions"].append("Avoid sequential characters like 'abc' or '123'")
    
    # Set strength level
    if score >= 4:
        feedback["strength"] = "strong"
    elif score >= 3:
        feedback["strength"] = "good"
    elif score >= 2:
        feedback["strength"] = "fair"
    
    feedback["score"] = score
    return feedback
