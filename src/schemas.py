from pydantic import BaseModel, EmailStr, Field
from datetime import date

from pydantic_settings import SettingsConfigDict

from src.database.models import Role


class ContactModel(BaseModel):
    firstname: str
    lastname: str
    email: EmailStr
    phone: str
    birthday: date | None = None


class ResponseContact(BaseModel):
    model_config = SettingsConfigDict(from_attributes=True)
    id: int
    firstname: str
    lastname: str
    email: EmailStr
    phone: str
    birthday: date | None


class ContactUpdateModel(BaseModel):
    email: EmailStr
    phone: str


class UserModel(BaseModel):
    username: str
    email: EmailStr
    password: str = Field(min_length=6, max_length=10)


class UserResponse(BaseModel):
    model_config = SettingsConfigDict(from_attributes=True)
    id: int
    username: str
    email: str
    avatar: str
    role: Role


class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RequestEmail(BaseModel):
    email: EmailStr
