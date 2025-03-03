from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User
from src.schemas.users import UserCreate


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.db = session

    async def get_user_by_id(self, user_id: int) -> User | None:
        """
        Retrieve a user by their ID.

        Args:
            user_id (int): The ID of the user.

        Returns:
            User | None: The user if found, otherwise None.
        """

        stmt = select(User).filter_by(id=user_id)
        user = await self.db.execute(stmt)
        return user.scalar_one_or_none()

    async def get_user_by_username(self, username: str) -> User | None:
        """
        Retrieve a user by their username.

        Args:
            username (str): The username to retrieve the user from.

        Returns:
            User | None: The user if found, otherwise None.
        """

        stmt = select(User).filter_by(username=username)
        user = await self.db.execute(stmt)
        return user.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> User | None:
        """
        Retrieve a user by their email.

        Args:
            email (str): The email to retrieve the user from.

        Returns:
            User | None: The user if found, otherwise None.
        """

        stmt = select(User).filter_by(email=email)
        user = await self.db.execute(stmt)
        return user.scalar_one_or_none()

    async def create_user(self, body: UserCreate, avatar: str = None) -> User:
        """
        Create a new user.

        Args:
            body (UserCreate): The user data to create the user.
            avatar (str, optional): The avatar URL for the user. Defaults to None.

        Returns:
            User: The created user.
        """

        user = User(
            **body.model_dump(exclude_unset=True, exclude={"password"}),
            hashed_password=body.password,
            avatar=avatar
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def confirmed_email(self, email: str) -> None:
        """
        Confirm the user's email.

        Args:
            email (str): The email of the user to confirm.

        Raises:
            ValueError: If the user is not found.
        """

        user = await self.get_user_by_email(email)
        user.confirmed = True
        await self.db.commit()

    async def update_avatar_url(self, email: str, url: str) -> User:
        """
        Update the user's avatar URL.

        Args:
            email (str): The email of the user.
            url (str): The new avatar URL.

        Returns:
            User: The updated user.
        """

        user = await self.get_user_by_email(email)
        user.avatar = url
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def update_password(self, email: str, new_password: str) -> User:
        """
        Update the user's password.

        Args:
            email (str): The email of the user.
            new_password (str): The new password to set.

        Returns:
            User: The updated user.
        """

        user = await self.get_user_by_email(email)
        user.hashed_password = new_password
        await self.db.commit()
        await self.db.refresh(user)
        return user
