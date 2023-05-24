from pydantic import BaseModel, EmailStr, Field


class RegisterIn(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str = Field(..., min_length=8)
