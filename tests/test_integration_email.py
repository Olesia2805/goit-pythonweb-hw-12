from unittest.mock import Mock
from fastapi import status

import pytest
from sqlalchemy import select

from src.database.models import User
from src.conf import messages
from tests.conftest import TestingSessionLocal
from src.services.users import UserService
from src.schemas.users import UserCreate
from src.services.email import send_email


@pytest.mark.asyncio
async def test_send_email_invalid_type():
    with pytest.raises(KeyError):
        await send_email(
            "test@example.com", "testuser", "http://example.com", "invalid_type"
        )
