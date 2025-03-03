from datetime import datetime, date

from sqlalchemy import Column, Integer, String, Boolean, func, Enum as SQLEnum  # type: ignore
from sqlalchemy.orm import relationship, mapped_column, Mapped, DeclarativeBase  # type: ignore
from sqlalchemy.sql.schema import ForeignKey, UniqueConstraint  # type: ignore
from sqlalchemy.sql.sqltypes import DateTime, Date  # type: ignore

import enum

# from src.database.db import engine


class Base(DeclarativeBase):
    """
    Base class for all models, providing created_at and updated_at timestamps.
    """

    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now()
    )


class Contact(Base):
    """
    Represents a contact entity with personal information and a relationship to a user.
    """

    __tablename__ = "contacts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False)
    phone_number: Mapped[str] = mapped_column(String(20), nullable=False)
    birthday: Mapped[date] = mapped_column(Date, nullable=False)
    additional_data: Mapped[str] = mapped_column(String(150), nullable=True)

    user_id = Column(
        "user_id", ForeignKey("users.id", ondelete="CASCADE"), default=None
    )
    user = relationship("User", backref="contacts")
    __table_args__ = (
        UniqueConstraint("first_name", "last_name", "user_id", name="unique_contact"),
    )


class UserRole(enum.Enum):
    """
    Enum for user roles.
    """

    USER = "user"
    ADMIN = "admin"


class User(Base):
    """
    Represents a user entity with authentication and profile information.
    """

    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=func.now())
    avatar = Column(String(255), nullable=True)
    confirmed = Column(Boolean, default=False)
    role = Column(SQLEnum(UserRole), default=UserRole.USER, nullable=False)
