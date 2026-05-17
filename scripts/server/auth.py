from datetime import datetime, timedelta, timezone
from typing import Optional, List, Dict, Any
import uuid
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import os

from .database import get_db
from .models import User, UserRole, RevokedAccessToken
from .jwt_key_rotation import JWTKeyRing

# Use Argon2 for password hashing
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/token")

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError(
        "SECRET_KEY environment variable is not set. "
        "Generate one with: python -c \"import secrets; print(secrets.token_hex(32))\""
    )
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# --- Scope Definitions ---
# Scopes define granular permissions for API access
SCOPES = {
    "read_jobs": "Read job status and results",
    "create_jobs": "Create and submit new jobs",
    "update_jobs": "Update job parameters",
    "delete_jobs": "Delete jobs",
    "admin": "Administrative access",
    "user:read": "Read user profile",
    "user:write": "Modify user profile",
    "export_data": "Export user data",
    "delete_account": "Delete user account",
}

# Default scopes for regular users
DEFAULT_USER_SCOPES = ["read_jobs", "create_jobs", "update_jobs", "user:read", "user:write", "export_data", "delete_account"]

# Scopes for admin users (includes all scopes except we explicitly list admin)
ADMIN_SCOPES = list(SCOPES.keys())


def utc_now() -> datetime:
    return datetime.now(timezone.utc)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)


def get_password_hash_scheme() -> str:
    schemes = pwd_context.schemes()
    return schemes[0] if schemes else "argon2"


def password_hash_needs_upgrade(hashed_password: str) -> bool:
    try:
        return pwd_context.needs_update(hashed_password)
    except Exception:
        return False


def _resolve_signing_key() -> tuple[str, Optional[str]]:
    """Get active JWT signing key and optional key id (kid)."""
    try:
        keyring = JWTKeyRing()
        current_key = keyring.get_current_key()
        current_kid = keyring.get_current_key_id()
        if current_key:
            return current_key, current_kid

        # Bootstrap keyring with existing SECRET_KEY for a smooth migration.
        keyring.rotate_key(SECRET_KEY)
        return keyring.get_current_key() or SECRET_KEY, keyring.get_current_key_id()
    except Exception:
        return SECRET_KEY, None


def _verification_keys() -> List[str]:
    """Return all valid verification keys, including legacy fallback key."""
    keys: List[str] = []
    try:
        keyring = JWTKeyRing()
        keys.extend([k for k in keyring.get_all_valid_keys() if k])
    except Exception:
        pass

    if SECRET_KEY not in keys:
        keys.append(SECRET_KEY)
    return keys

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None, scopes: Optional[List[str]] = None):
    to_encode = data.copy()
    now = utc_now()
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    if scopes is None:
        scopes = DEFAULT_USER_SCOPES
    
    to_encode.update({
        "exp": expire,
        "iat": now,
        "type": "access",
        "jti": uuid.uuid4().hex,
        "scopes": scopes,  # Add scopes to token
    })
    signing_key, key_id = _resolve_signing_key()
    headers = {"kid": key_id} if key_id else None
    encoded_jwt = jwt.encode(to_encode, signing_key, algorithm=ALGORITHM, headers=headers)
    return encoded_jwt


def decode_token_payload(token: str) -> Dict[str, Any]:
    last_error: Optional[Exception] = None
    for key in _verification_keys():
        try:
            return jwt.decode(token, key, algorithms=[ALGORITHM])
        except JWTError as exc:
            last_error = exc
            continue

    if last_error:
        raise last_error
    raise JWTError("Token verification failed")


def parse_access_token(token: str) -> Dict[str, Any]:
    try:
        payload = decode_token_payload(token)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = parse_access_token(token)
        email: str = payload.get("sub")
        jti: str = payload.get("jti")
        if email is None:
            raise credentials_exception
        if not jti:
            raise credentials_exception
    except (JWTError, HTTPException):
        raise credentials_exception

    revoked = db.query(RevokedAccessToken).filter(RevokedAccessToken.jti == jti).first()
    if revoked:
        raise credentials_exception

    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    return user


def get_current_user_with_scopes(required_scopes: List[str]):
    """
    Dependency factory that creates a function to check if current user has required scopes.
    
    Usage:
        @app.get("/some-endpoint")
        async def endpoint(user: User = Depends(get_current_user_with_scopes(["create_jobs"]))):
            ...
    """
    async def check_scopes(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
        credentials_exception = HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = parse_access_token(token)
            email: str = payload.get("sub")
            jti: str = payload.get("jti")
            token_scopes: List[str] = payload.get("scopes", [])
            
            if email is None or not jti:
                raise credentials_exception
                
            # Check if token has all required scopes
            if not all(scope in token_scopes for scope in required_scopes):
                raise credentials_exception
        except (JWTError, HTTPException):
            raise credentials_exception

        revoked = db.query(RevokedAccessToken).filter(RevokedAccessToken.jti == jti).first()
        if revoked:
            raise credentials_exception

        user = db.query(User).filter(User.email == email).first()
        if user is None:
            raise credentials_exception
        return user
    
    return check_scopes

def check_role(roles: List[UserRole]):
    async def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have enough permissions"
            )
        return current_user
    return role_checker
