from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.conf import messages
from src.database.db import get_db
from src.database.models import User
from src.schemas.contacts import ContactBase, ContactBirthdayRequest, ContactResponse
from src.services.auth import get_current_user
from src.services.contacts import ContactService

router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.get("/", response_model=List[ContactResponse], status_code=status.HTTP_200_OK)
async def read_contacts(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Retrieve a list of contacts.

    Args:
    skip: int (optional): Skip the first `skip` contacts. Defaults to 0.
    limit: int (optional): Limit the number of contacts returned. Defaults to 100.
    db: AsyncSession: Database session.
    user: User: Current authenticated user.

    Returns:
    List[ContactResponse]: List of contacts.
    """

    contact_service = ContactService(db)
    contacts = await contact_service.get_contacts(skip, limit, user)
    return contacts


@router.get("/{contact_id}", response_model=ContactResponse)
async def read_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Retrieve a specific contact by ID.

    Args:
    contact_id: int: Contact ID.
    db: AsyncSession: Database session.
    user: User: Current authenticated user.

    Returns:
    ContactResponse: Specific contact.
    """

    contact_service = ContactService(db)
    contact = await contact_service.get_contact(contact_id, user)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.CONTACT_NOT_FOUND
        )
    return contact


@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(
    body: ContactBase,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Create a new contact.

    Args:
    body: ContactBase: New contact data.
    db: AsyncSession: Database session.
    user: User: Current authenticated user.

    Returns:
    ContactResponse: Created contact.

    Raises:
    HTTPException: If the contact already exists.
    """

    contact_service = ContactService(db)
    return await contact_service.create_contact(body, user)


@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(
    body: ContactBase,
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Update a specific contact by ID.

    Args:
    contact_id: int: Contact ID.
    body: ContactBase: Updated contact data.
    db: AsyncSession: Database session.
    user: User: Current authenticated user.

    Returns:
    ContactResponse: Updated contact.

    Raises:
    HTTPException: If the contact does not exist.
    """

    contact_service = ContactService(db)
    contact = await contact_service.update_contact(contact_id, body, user)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.CONTACT_NOT_FOUND
        )
    return contact


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Remove a specific contact by ID.

    Args:
    contact_id: int: Contact ID.
    db: AsyncSession: Database session.
    user: User: Current authenticated user.

    Returns:
    ContactResponse: Removed contact.

    Raises:
    HTTPException: If the contact does not exist.
    """

    contact_service = ContactService(db)
    contact = await contact_service.remove_contact(contact_id, user)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.CONTACT_NOT_FOUND
        )
    return


@router.get(
    "/search/", response_model=List[ContactResponse], status_code=status.HTTP_200_OK
)
async def search_contacts(
    text: str,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Retrieve a list of contacts whose names or email addresses contain the specified search query.

    Args:
    text: str: Search query.
    skip: int (optional): Skip the first `skip` contacts. Defaults to 0.
    limit: int (optional): Limit the number of contacts returned. Defaults to 100.
    db: AsyncSession: Database session.
    user: User: Current authenticated user.

    Returns:
    List[ContactResponse]: List of contacts whose names or email addresses contain the specified search query.
    """

    contact_service = ContactService(db)
    contacts = await contact_service.search_contacts(text, skip, limit, user)
    return contacts


@router.post("/upcoming-birthdays", response_model=List[ContactResponse])
async def upcoming_birthdays(
    body: ContactBirthdayRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Retrieve a list of contacts whose birthday is within the specified number of days.

    Args:
    body: ContactBirthdayRequest: Request body containing the number of days.
    db: AsyncSession: Database session.
    user: User: Current authenticated user.

    Returns:
    List[ContactResponse]: List of contacts whose birthday is within the specified number of days.
    """

    contact_service = ContactService(db)
    contacts = await contact_service.upcoming_birthdays(body.days, user)
    return contacts
