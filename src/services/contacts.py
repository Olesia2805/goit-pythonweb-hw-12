from sqlalchemy.ext.asyncio import AsyncSession  # type: ignore

from src.database.models import User
from src.repository.contacts import ContactRepository
from src.schemas.contacts import ContactBase


class ContactService:
    def __init__(self, db: AsyncSession):
        """
        Initialize the ContactService with a database session.

        Args:
            db (AsyncSession): The database session.
        """
        self.contact_repository = ContactRepository(db)

    async def create_contact(self, body: ContactBase, user: User):
        """
        Create a new contact.

        Args:
            body (ContactBase): The contact data.
            user (User): The user creating the contact.

        Returns:
            Contact: The created contact.
        """
        return await self.contact_repository.create_contact(body, user)

    async def get_contacts(self, skip: int, limit: int, user: User):
        """
        Get a list of contacts.

        Args:
            skip (int): The number of contacts to skip.
            limit (int): The maximum number of contacts to return.
            user (User): The user retrieving the contacts.

        Returns:
            List[Contact]: The list of contacts.
        """
        return await self.contact_repository.get_contacts(skip, limit, user)

    async def get_contact(self, contact_id: int, user: User):
        """
        Get a specific contact by ID.

        Args:
            contact_id (int): The contact ID.
            user (User): The user retrieving the contact.

        Returns:
            Contact | None: The contact if found, otherwise None.
        """
        return await self.contact_repository.get_contact_by_id(contact_id, user)

    async def update_contact(self, contact_id: int, body: ContactBase, user: User):
        """
        Update a specific contact by ID.

        Args:
            contact_id (int): The contact ID.
            body (ContactBase): The updated contact data.
            user (User): The user updating the contact.

        Returns:
            Contact | None: The updated contact if found, otherwise None.
        """
        return await self.contact_repository.update_contact(contact_id, body, user)

    async def remove_contact(self, contact_id: int, user: User):
        """
        Remove a specific contact by ID.

        Args:
            contact_id (int): The contact ID.
            user (User): The user removing the contact.

        Returns:
            Contact | None: The removed contact if found, otherwise None.
        """
        return await self.contact_repository.remove_contact(contact_id, user)

    async def search_contacts(self, search: str, skip: int, limit: int, user: User):
        """
        Search for contacts.

        Args:
            search (str): The search query.
            skip (int): The number of contacts to skip.
            limit (int): The maximum number of contacts to return.
            user (User): The user searching for contacts.

        Returns:
            List[Contact]: The list of contacts matching the search query.
        """
        return await self.contact_repository.search_contacts(search, skip, limit, user)

    async def upcoming_birthdays(self, days: int, user: User):
        """
        Get contacts with upcoming birthdays.

        Args:
            days (int): The number of days to check for upcoming birthdays.
            user (User): The user retrieving the contacts.

        Returns:
            List[Contact]: The list of contacts with upcoming birthdays.
        """
        return await self.contact_repository.upcoming_birthdays(days, user)
