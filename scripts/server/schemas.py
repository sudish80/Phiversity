from pydantic import BaseModel, Field
from typing import Optional

class RunRequest(BaseModel):
    problem: str = Field(..., min_length=1, max_length=4096, description="The problem or question to solve")
    mode: str = Field("question_solving", pattern="^(question_solving|lecture|revision)$", description="Learning mode")
    orchestrate: bool = True
    voice_first: bool = False
    element_audio: bool = False
    long_video: bool = False
    custom_prompt: Optional[str] = Field(None, max_length=8192)
    idempotency_key: Optional[str] = Field(None, max_length=128, description="Optional client-supplied key to prevent duplicate jobs")

class JobResponse(BaseModel):
    job_id: str
    status: str

class JobStatusResponse(BaseModel):
    status: str
    log: str
    progress: int
    video_url: Optional[str] = None
    plan_url: Optional[str] = None
    log_url: Optional[str] = None

class UserCreate(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class UserResponse(BaseModel):
    id: int
    email: str
    role: str

class LoginRequest(BaseModel):
    email: str
    password: str

class ForgotPasswordRequest(BaseModel):
    email: str
