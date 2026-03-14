from pydantic import BaseModel, ConfigDict, EmailStr, Field
from datetime import datetime


class UserCreate(BaseModel):
    username: str = Field(min_length=1, max_length=25)
    email: EmailStr
    password: str = Field(min_length=6)

class UserUpdate(BaseModel):
    username: str | None = Field(default=None, min_length=1, max_length=25)
    email: EmailStr | None = Field(default=None)
    password: str | None = Field(default=None, min_length=6)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    is_active: bool
    is_admin: bool

    model_config = ConfigDict(from_attributes=True)