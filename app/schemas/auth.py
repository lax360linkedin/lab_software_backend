from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class SignupRequest(BaseModel):
    labName: str = Field(..., min_length=1, max_length=200, description="Name of the laboratory")
    adminName: str = Field(..., min_length=1, max_length=100, description="Name of primary administrator")
    email: EmailStr = Field(..., description="Administrator email address")
    phone: str = Field(..., min_length=5, max_length=20, description="Contact phone number")
    address: str = Field(..., min_length=1, max_length=500, description="Laboratory address")
    password: str = Field(..., min_length=8, max_length=128, description="Account password (min 8 chars)")
    confirmPassword: Optional[str] = Field(None, description="Password confirmation if provided")


class SignupResponse(BaseModel):
    message: str = "Laboratory account created successfully"


class LoginRequest(BaseModel):
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=1, description="User password")


class UserResponse(BaseModel):
    userId: str
    labId: str
    labName: str
    name: str
    email: str
    role: str


class LoginResponse(BaseModel):
    accessToken: str
    tokenType: str = "bearer"
    user: UserResponse


class TokenPayload(BaseModel):
    sub: Optional[str] = None
    userId: str
    labId: str
    role: str
    exp: Optional[int] = None
