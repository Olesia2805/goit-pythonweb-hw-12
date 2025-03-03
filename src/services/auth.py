from datetime import datetime, timedelta, UTC
from typing import Optional

from fastapi import Depends, HTTPException, status
from passlib.context import CryptContext
from fastapi.security import (
    HTTPBearer,
    HTTPAuthorizationCredentials,
)
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError, jwt
import redis
from redis_lru import RedisLRU
import logging

from src.database.db import get_db
from src.conf.config import settings
from src.services.users import UserService
from src.schemas.users import User, UserRole

from src.conf import messages

client = redis.StrictRedis(host="localhost", port=6379, password=None)
redis = RedisLRU(client, default_ttl=10 * 60)

logging.basicConfig(level=logging.INFO)


class Hash:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def verify_password(self, plain_password, hashed_password):
        """
        Verify a plain password against a hashed password.

        Args:
            plain_password (str): The plain password.
            hashed_password (str): The hashed password.

        Returns:
            bool: True if the password matches, False otherwise.
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str):
        """
        Hash a plain password.

        Args:
            password (str): The plain password.

        Returns:
            str: The hashed password.
        """
        return self.pwd_context.hash(password)


oauth2_scheme = HTTPBearer()


async def create_access_token(data: dict, expires_delta: Optional[int] = None):
    """
    Create a JWT access token.

    Args:
        data (dict): The data to encode in the token.
        expires_delta (Optional[int]): The expiration time in seconds. Defaults to None.

    Returns:
        str: The encoded JWT token.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + timedelta(seconds=expires_delta)
    else:
        expire = datetime.now(UTC) + timedelta(seconds=settings.JWT_EXPIRATION_SECONDS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


async def get_current_user(
    token: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
):
    """
    Get the current authenticated user from the JWT token.

    Args:
        token (HTTPAuthorizationCredentials): The JWT token.
        db (AsyncSession): The database session.

    Returns:
        User: The authenticated user.

    Raises:
        HTTPException: If the token is invalid or the user is not found.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=messages.INVALID_CREDENTIALS,
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token.credentials, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError as e:
        raise credentials_exception

    # logging.info("Checking user: " + username)

    cache_key = f"user:{username}"
    cached_user = redis.get(cache_key)

    if cached_user:
        logging.info("User found in cache: " + username)
        return cached_user

    # logging.info("User not found in cache, fetching from database: " + username)

    user_service = UserService(db)
    user = await user_service.get_user_by_username(username)

    if user is None:
        raise credentials_exception

    # logging.info("User saved to cache: " + username)

    redis.set(cache_key, user)
    return user


def create_email_token(data: dict):
    """
    Create a JWT token for email verification.

    Args:
        data (dict): The data to encode in the token.

    Returns:
        str: The encoded JWT token.
    """
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(days=7)
    to_encode.update({"iat": datetime.now(UTC), "exp": expire})
    token = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return token


async def get_email_from_token(token: str):
    """
    Get the email from the JWT token.

    Args:
        token (str): The JWT token.

    Returns:
        str: The email extracted from the token.

    Raises:
        HTTPException: If the token is invalid.
    """
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        email = payload.get("sub")
        return email

    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=messages.INVALID_EMAIL_TOKEN,
        )


def get_current_user_role(current_user: dict):
    """
    Get the role of the current authenticated user.

    Args:
        current_user (dict): The current authenticated user.

    Returns:
        dict: The current authenticated user.

    Raises:
        HTTPException: If the user does not have the required role.
    """
    if current_user["role"] != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=messages.ACCESS_DENIED,
        )
    return current_user
