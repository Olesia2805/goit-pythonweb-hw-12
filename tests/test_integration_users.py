import pytest
from unittest.mock import AsyncMock
from src.services.users import UserService


@pytest.mark.asyncio
async def test_get_user_by_id_not_found():
    user_id = 999
    mock_repository = AsyncMock()
    mock_repository.get_user_by_id.return_value = None
    user_service = UserService(AsyncMock())
    user_service.repository = mock_repository

    result = await user_service.get_user_by_id(user_id)

    assert result is None
    mock_repository.get_user_by_id.assert_called_once_with(user_id)


@pytest.mark.asyncio
async def test_confirmed_email_returns_true():
    email = "test@example.com"
    mock_repository = AsyncMock()
    mock_repository.confirmed_email.return_value = True
    user_service = UserService(AsyncMock())
    user_service.repository = mock_repository

    result = await user_service.confirmed_email(email)

    assert result is True
    mock_repository.confirmed_email.assert_called_once_with(email)


@pytest.mark.asyncio
async def test_update_avatar_url():
    email = "test@example.com"
    new_url = "new_url.jpg"
    updated_user = {"email": email, "avatar": new_url}
    mock_repository = AsyncMock()
    mock_repository.update_avatar_url.return_value = updated_user
    user_service = UserService(AsyncMock())
    user_service.repository = mock_repository

    result = await user_service.update_avatar_url(email, new_url)

    assert result == updated_user
    mock_repository.update_avatar_url.assert_called_once_with(email, new_url)


@pytest.mark.asyncio
async def test_update_password():
    email = "test@example.com"
    new_password = "new_password"
    mock_repository = AsyncMock()
    mock_repository.update_password.return_value = True
    user_service = UserService(AsyncMock())
    user_service.repository = mock_repository

    result = await user_service.update_password(email, new_password)
    assert result is True
    mock_repository.update_password.assert_called_once_with(email, new_password)
