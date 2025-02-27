from pydantic import BaseModel, ConfigDict, EmailStr
from src.database.models import UserRole


class User(BaseModel):
    id: int
    username: str
    email: EmailStr
    avatar: str
    role: UserRole

    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    # role: UserRole


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class RequestEmail(BaseModel):
    email: EmailStr
