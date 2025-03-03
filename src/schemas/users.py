from pydantic import BaseModel, ConfigDict, EmailStr
from src.database.models import UserRole


class User(BaseModel):
    """
    Schema for representing a user.
    """

    id: int
    username: str
    email: EmailStr
    avatar: str
    role: UserRole

    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    """
    Schema for creating a new user.
    """

    username: str
    email: EmailStr
    password: str
    role: UserRole


class UserLogin(BaseModel):
    """
    Schema for user login.
    """

    email: EmailStr
    password: str


class Token(BaseModel):
    """
    Schema for representing an authentication token.
    """

    access_token: str
    token_type: str


class RequestEmail(BaseModel):
    """
    Schema for requesting an email.
    """

    email: EmailStr
