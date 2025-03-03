from datetime import timedelta
from typing import List

from sqlalchemy import Integer, and_, extract, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.database.models import Contact, User
from src.schemas.contacts import ContactBase, ContactResponse


class ContactRepository:
    def __init__(self, session: AsyncSession):
        self.db = session

    async def get_contacts(self, skip: int, limit: int, user: User) -> List[Contact]:
        """
        Get contacts for the specified user, paginated.

        Args:
            skip (int): The offset for pagination.
            limit (int): The number of contacts to return per page.
            user (User): The user to get the contacts for.
        """

        stmt = select(Contact).filter_by(user=user).offset(skip).limit(limit)
        contacts = await self.db.execute(stmt)
        return contacts.scalars().all()

    async def get_contact_by_id(self, contact_id: int, user: User) -> Contact | None:
        """
        Get a specific contact by ID for the specified user.

        Args:
            contact_id (int): Contact ID.
            user (User): The user to get the contact for.
        """

        stmt = select(Contact).filter_by(user=user, id=contact_id)
        contact = await self.db.execute(stmt)
        return contact.scalar_one_or_none()

    async def create_contact(self, body: ContactBase, user: User) -> Contact:
        """
        Create a new contact for the specified user.

        Args:
            body (ContactBase): New contact data.
            user (User): The user to create the contact for.
        """

        contact = Contact(**body.model_dump(exclude_unset=True), user=user)
        self.db.add(contact)
        await self.db.commit()
        await self.db.refresh(contact)
        return contact

    async def remove_contact(self, contact_id: int, user: User) -> Contact | None:
        """
        Remove a specific contact by ID.

        Args:
            contact_id (int): Contact ID.
            user (User): The user to remove the contact for.
        """

        contact = await self.get_contact_by_id(contact_id, user)
        if contact:
            await self.db.delete(contact)
            await self.db.commit()
        return contact

    async def update_contact(
        self, contact_id: int, body: ContactBase, user: User
    ) -> Contact | None:
        """
        Update a specific contact by ID.

        Args:
            contact_id (int): Contact ID.
            body (ContactBase): Updated contact data.
            user (User): The user to update the contact for.
        """

        contact = await self.get_contact_by_id(contact_id, user)
        if contact:
            for key, value in body.dict(exclude_unset=True).items():
                setattr(contact, key, value)

            await self.db.commit()
            await self.db.refresh(contact)

        return contact

    async def search_contacts(
        self, search: str, skip: int, limit: int, user: User
    ) -> List[Contact]:
        """
        Search contacts for the specified user, paginated.

        Args:
            search (str): The search query.
            skip (int): The offset for pagination.
            limit (int): The number of contacts to return per page.
            user (User): The user to search the contacts for.
        """

        stmt = (
            select(Contact)
            .filter(
                Contact.user == user,
                or_(
                    Contact.first_name.ilike(f"%{search}%"),
                    Contact.last_name.ilike(f"%{search}%"),
                    Contact.email.ilike(f"%{search}%"),
                    Contact.additional_data.ilike(f"%{search}%"),
                    Contact.phone_number.ilike(f"%{search}%"),
                ),
            )
            .offset(skip)
            .limit(limit)
        )
        contacts = await self.db.execute(stmt)
        return contacts.scalars().all()

    async def upcoming_birthdays(self, days: int, user: User) -> List[Contact]:
        """
        Get contacts whose birthday is within the specified number of days.

        Args:
            days (int): The number of days to check for upcoming birthdays.
            user (User): The user to get the upcoming birthdays for.
        """

        today = func.current_date()
        future_date = func.current_date() + timedelta(days=days)

        stmt = select(Contact).filter(
            Contact.user == user,
            or_(
                func.make_date(
                    extract("year", today).cast(Integer),
                    extract("month", Contact.birthday).cast(Integer),
                    extract("day", Contact.birthday).cast(Integer),
                ).between(today, future_date),
                func.make_date(
                    (extract("year", today) + 1).cast(Integer),
                    extract("month", Contact.birthday).cast(Integer),
                    extract("day", Contact.birthday).cast(Integer),
                ).between(today, future_date),
            ),
        )
        contacts = await self.db.execute(stmt)
        return contacts.scalars().all()
