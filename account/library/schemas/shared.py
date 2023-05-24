from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr


class CoreModel(BaseModel):
    id: UUID
    created_at: datetime


class UserPublic(CoreModel):
    email: EmailStr
    first_name: str
    last_name: str
    is_verified: bool


class StatusResponse(BaseModel):
    message: str
