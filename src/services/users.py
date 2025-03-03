from sqlalchemy.ext.asyncio import AsyncSession  # type: ignore
from libgravatar import Gravatar  # type: ignore

from src.repository.users import UserRepository
from src.schemas.users import UserCreate
import logging


class UserService:
    def __init__(self, db: AsyncSession):
        """
        Initialize the UserService with a database session.

        Args:
            db (AsyncSession): The database session.
        """
        self.repository = UserRepository(db)

    async def create_user(self, body: UserCreate):
        """
        Create a new user.

        Args:
            body (UserCreate): The user data.

        Returns:
            User: The created user.
        """
        avatar = None
        try:
            g = Gravatar(body.email)
            avatar = g.get_image()
        except Exception as e:
            logging.error(f"Error occurred while fetching avatar: {e}")

        return await self.repository.create_user(body, avatar)

    async def get_user_by_id(self, user_id: int):
        """
        Get a user by their ID.

        Args:
            user_id (int): The user ID.

        Returns:
            User | None: The user if found, otherwise None.
        """
        return await self.repository.get_user_by_id(user_id)

    async def get_user_by_username(self, username: str):
        """
        Get a user by their username.

        Args:
            username (str): The username.

        Returns:
            User | None: The user if found, otherwise None.
        """
        return await self.repository.get_user_by_username(username)

    async def get_user_by_email(self, email: str):
        """
        Get a user by their email.

        Args:
            email (str): The email.

        Returns:
            User | None: The user if found, otherwise None.
        """
        return await self.repository.get_user_by_email(email)

    async def confirmed_email(self, email: str):
        """
        Confirm a user's email.

        Args:
            email (str): The email to confirm.

        Returns:
            None
        """
        return await self.repository.confirmed_email(email)

    async def update_avatar_url(self, email: str, url: str):
        """
        Update a user's avatar URL.

        Args:
            email (str): The user's email.
            url (str): The new avatar URL.

        Returns:
            User: The updated user.
        """
        return await self.repository.update_avatar_url(email, url)

    async def update_password(self, email: str, password: str):
        """
        Update a user's password.

        Args:
            email (str): The user's email.
            password (str): The new password.

        Returns:
            User: The updated user.
        """
        return await self.repository.update_password(email, password)
