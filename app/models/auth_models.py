from pydantic import BaseModel
from typing import Optional


class SignupRequest(BaseModel):
    name: str
    email: str
    password: str
    role: str   # Nurse / Doctor / Paramedic


class LoginRequest(BaseModel):
    email: str
    password: str


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    role: str
