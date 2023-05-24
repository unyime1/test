from typing import List

from pydantic import BaseModel, EmailStr, Field
from library.schemas.shared import UserPublic


class TokenData(BaseModel):
    """
    Define token encoding structure.
    """

    user_id: str
    scopes: List[str] = []


class AuthResponse(BaseModel):
    """Authentication response."""

    user: UserPublic
    access_token: str


class LoginSchema(BaseModel):
    """Login data schema."""

    email: EmailStr
    password: str


class ConfirmPasswordReset(BaseModel):
    """Confirm password reset."""

    otp: str
    new_password: str = Field(..., min_length=8)
