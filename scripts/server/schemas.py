import re
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List

# Data sanitization patterns
SANITIZE_STRIP_PATTERN = re.compile(r'[<>\"\'%;()&+]')
SANITIZE_EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

def sanitize_input(value: str, max_length: int = 4096) -> str:
    """Sanitize user input by removing potentially dangerous characters."""
    if not value:
        return value
    # Strip dangerous characters
    sanitized = SANITIZE_STRIP_PATTERN.sub('', value)
    # Normalize whitespace
    sanitized = ' '.join(sanitized.split())
    # Truncate to max length
    return sanitized[:max_length]

def sanitize_email(email: str) -> str:
    """Sanitize and validate email format."""
    if not email:
        return email
    # Lowercase and strip
    email = email.lower().strip()
    # Remove any characters not allowed in emails
    email = re.sub(r'[^a-z0-9._%+-@]', '', email)
    return email


class RunRequest(BaseModel):
    problem: str = Field(..., min_length=1, max_length=4096, description="The problem or question to solve")
    mode: str = Field("question_solving", pattern="^(question_solving|lecture|revision)$", description="Learning mode")
    orchestrate: bool = True
    voice_first: bool = False
    element_audio: bool = False
    long_video: bool = False
    custom_prompt: Optional[str] = Field(None, max_length=8192)
    idempotency_key: Optional[str] = Field(None, max_length=128, description="Optional client-supplied key to prevent duplicate jobs")
    
    @field_validator('problem', 'custom_prompt', mode='before')
    @classmethod
    def sanitize_problem(cls, v):
        if v:
            return sanitize_input(v)
        return v
    
    @field_validator('idempotency_key', mode='before')
    @classmethod
    def sanitize_idempotency_key(cls, v):
        if v:
            # Only allow alphanumeric and hyphens/underscores
            return re.sub(r'[^a-zA-Z0-9_-]', '', v)[:128]
        return v


class JobResponse(BaseModel):
    job_id: str
    status: str


class JobSummaryResponse(BaseModel):
    status: str
    failed_stage: str
    exit_code: int
    total_duration_seconds: int
    stage_durations_seconds: dict[str, int] = Field(default_factory=dict)
    next_action_hint: str


class JobStatusResponse(BaseModel):
    status: str
    log: str
    progress: int
    video_url: Optional[str] = None
    plan_url: Optional[str] = None
    log_url: Optional[str] = None
    summary: Optional[JobSummaryResponse] = None


class UserCreate(BaseModel):
    email: str = Field(..., min_length=5, max_length=254, description="User email address")
    password: str = Field(..., min_length=8, max_length=128, description="User password")
    username: Optional[str] = Field(None, min_length=3, max_length=64, description="Optional unique username")
    full_name: Optional[str] = Field(None, min_length=1, max_length=120, description="Optional display name")
    phone_number: Optional[str] = Field(None, min_length=5, max_length=32, description="Optional contact phone")
    signup_source: Optional[str] = Field("email", min_length=2, max_length=32, description="Signup source channel")
    
    @field_validator('email', mode='before')
    @classmethod
    def sanitize_email(cls, v):
        if v:
            return sanitize_email(v)
        return v

    @field_validator('username', mode='before')
    @classmethod
    def sanitize_username(cls, v):
        if v:
            return re.sub(r'[^a-zA-Z0-9_.-]', '', str(v)).strip().lower()[:64]
        return v

    @field_validator('full_name', mode='before')
    @classmethod
    def sanitize_full_name(cls, v):
        if v:
            return sanitize_input(str(v), max_length=120)
        return v

    @field_validator('phone_number', mode='before')
    @classmethod
    def sanitize_phone_number(cls, v):
        if v:
            return re.sub(r'[^0-9+\-()\s]', '', str(v)).strip()[:32]
        return v

    @field_validator('signup_source', mode='before')
    @classmethod
    def sanitize_signup_source(cls, v):
        if v:
            return re.sub(r'[^a-zA-Z0-9_.-]', '', str(v)).strip().lower()[:32]
        return 'email'
    
    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        # Check for complexity (at least 2 of 3: upper, lower, digit)
        has_upper = any(c.isupper() for c in v)
        has_lower = any(c.islower() for c in v)
        has_digit = any(c.isdigit() for c in v)
        complexity_count = sum([has_upper, has_lower, has_digit])
        if complexity_count < 2 and len(v) < 12:
            raise ValueError('Password must have at least 8 characters with mixed case and numbers')
        return v


class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    email: str
    role: str
    quality_tier: str = "free"
    watermark_enabled: bool = True


class LoginRequest(BaseModel):
    email: str = Field(..., min_length=5, max_length=254)
    password: str = Field(..., min_length=1, max_length=128)
    
    @field_validator('email', mode='before')
    @classmethod
    def sanitize_email(cls, v):
        if v:
            return sanitize_email(v)
        return v


class ForgotPasswordRequest(BaseModel):
    email: str = Field(..., min_length=5, max_length=254)
    
    @field_validator('email', mode='before')
    @classmethod
    def sanitize_email(cls, v):
        if v:
            return sanitize_email(v)
        return v


class ResetPasswordRequest(BaseModel):
    token: str = Field(..., min_length=20, max_length=512)
    new_password: str = Field(..., min_length=8, max_length=256)
    
    @field_validator('new_password')
    @classmethod
    def validate_password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        has_upper = any(c.isupper() for c in v)
        has_lower = any(c.islower() for c in v)
        has_digit = any(c.isdigit() for c in v)
        complexity_count = sum([has_upper, has_lower, has_digit])
        if complexity_count < 2 and len(v) < 12:
            raise ValueError('Password must have at least 8 characters with mixed case and numbers')
        return v


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(..., min_length=20, max_length=512)
    
    @field_validator('refresh_token', mode='before')
    @classmethod
    def sanitize_token(cls, v):
        if v:
            return re.sub(r'[^a-zA-Z0-9_.-]', '', v)
        return v


class LogoutRequest(BaseModel):
    refresh_token: Optional[str] = Field(None, min_length=20, max_length=512)
    
    @field_validator('refresh_token', mode='before')
    @classmethod
    def sanitize_token(cls, v):
        if v:
            return re.sub(r'[^a-zA-Z0-9_.-]', '', v)
        return v


class MFAConfirmRequest(BaseModel):
    code: str = Field(..., min_length=6, max_length=8)

    @field_validator('code', mode='before')
    @classmethod
    def sanitize_code(cls, v):
        if v:
            return re.sub(r'[^0-9]', '', str(v))
        return v


class MFABackupRequest(BaseModel):
    backup_code: str = Field(..., min_length=5, max_length=32)

    @field_validator('backup_code', mode='before')
    @classmethod
    def sanitize_backup_code(cls, v):
        if v:
            return re.sub(r'[^A-Za-z0-9-]', '', str(v)).upper()
        return v


class APIKeyCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=80)
    scopes: List[str] = Field(default_factory=list, max_length=20)
    expires_days: Optional[int] = Field(default=None, ge=1, le=3650)

    @field_validator('name', mode='before')
    @classmethod
    def sanitize_name(cls, v):
        if v:
            return sanitize_input(v, max_length=80)
        return v


class APIKeyVerifyRequest(BaseModel):
    api_key: str = Field(..., min_length=16, max_length=256)


class APIKeyRevokeRequest(BaseModel):
    key_id: int = Field(..., ge=1)


class PasswordlessRequest(BaseModel):
    email: str = Field(..., min_length=5, max_length=254)

    @field_validator('email', mode='before')
    @classmethod
    def sanitize_email_value(cls, v):
        if v:
            return sanitize_email(v)
        return v


class PasswordlessVerifyRequest(BaseModel):
    token: str = Field(..., min_length=20, max_length=512)

    @field_validator('token', mode='before')
    @classmethod
    def sanitize_token_value(cls, v):
        if v:
            return re.sub(r'[^a-zA-Z0-9_.-]', '', str(v))
        return v


class OAuthClientCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    redirect_uris: List[str] = Field(default_factory=list)
    scopes: List[str] = Field(default_factory=list)
    grants: List[str] = Field(default_factory=lambda: ["authorization_code", "client_credentials"])


class WebAuthnRegisterVerifyRequest(BaseModel):
    challenge: str = Field(..., min_length=8, max_length=512)
    credential_id: str = Field(..., min_length=8, max_length=512)
    public_key: str = Field(..., min_length=16, max_length=8192)
    sign_count: int = Field(default=0, ge=0)
    aaguid: Optional[str] = Field(default=None, max_length=128)
    transports: List[str] = Field(default_factory=list)


class WebAuthnAuthenticateRequest(BaseModel):
    email: str = Field(..., min_length=5, max_length=254)
    credential_id: str = Field(..., min_length=8, max_length=512)
    challenge: str = Field(..., min_length=8, max_length=512)

    @field_validator('email', mode='before')
    @classmethod
    def sanitize_webauthn_email(cls, v):
        if v:
            return sanitize_email(v)
        return v


class SAMLProviderCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    entity_id: str = Field(..., min_length=1, max_length=512)
    sso_url: str = Field(..., min_length=8, max_length=1024)
    x509_cert: str = Field(..., min_length=16, max_length=20000)
    acs_url: Optional[str] = Field(default=None, max_length=1024)


class SAMLACSRequest(BaseModel):
    saml_response: str = Field(..., min_length=8, max_length=500000)
    relay_state: Optional[str] = Field(default=None, max_length=1024)
    email_hint: Optional[str] = Field(default=None, max_length=254)

    @field_validator('email_hint', mode='before')
    @classmethod
    def sanitize_saml_email_hint(cls, v):
        if v:
            return sanitize_email(v)
        return v
