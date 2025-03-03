import pytest
from src.services.email import send_email


@pytest.mark.asyncio
async def test_send_email_invalid_type():
    with pytest.raises(KeyError):
        await send_email(
            "test@example.com", "testuser", "http://example.com", "invalid_type"
        )
