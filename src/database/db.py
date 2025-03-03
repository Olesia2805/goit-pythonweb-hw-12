import contextlib

from sqlalchemy.exc import SQLAlchemyError  # type: ignore
from sqlalchemy.ext.asyncio import (  # type: ignore
    AsyncEngine,
    async_sessionmaker,
    create_async_engine,
)

from src.configuration.config import settings
from src.configuration import messages


class DatabaseSessionManager:
    """
    Manages the database session lifecycle.
    """

    def __init__(self, url: str):
        """
        Initializes the DatabaseSessionManager with the given database URL.
        """
        self._engine: AsyncEngine | None = create_async_engine(url)
        self._session_maker: async_sessionmaker = async_sessionmaker(
            autoflush=False, autocommit=False, bind=self._engine
        )

    @contextlib.asynccontextmanager
    async def session(self):
        """
        Provides a transactional scope around a series of operations.

        Raises:
            Exception: If the session maker is not initialized.
            SQLAlchemyError: If there is an error during the session.
        """
        if self._session_maker is None:
            raise Exception(messages.DATABASE_SESSION_NOT_INITIALIZED)
        session = self._session_maker()
        try:
            yield session
        except SQLAlchemyError as e:
            await session.rollback()
            raise
        finally:
            await session.close()


sessionmanager = DatabaseSessionManager(settings.DB_URL)


async def get_db():
    """
    Dependency function that provides a database session for request handlers.
    """
    async with sessionmanager.session() as session:
        yield session
