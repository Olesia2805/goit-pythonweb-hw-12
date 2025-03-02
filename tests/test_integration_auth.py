from unittest.mock import Mock
from fastapi import status, HTTPException

import pytest
from sqlalchemy import select

from src.database.models import User, UserRole
from src.conf import messages
from tests.conftest import TestingSessionLocal
from src.services.users import UserService
from src.schemas.users import UserCreate
from src.services.auth import get_current_user_role

user_data = {
    "username": "agent007",
    "email": "agent007@gmail.com",
    "password": "12345678",
    "role": UserRole.USER.value,
}

admin_data = {
    "username": "Tina037",
    "email": "Tina037@gmail.com",
    "password": "785632149",
    "role": UserRole.ADMIN.value,
}


def test_signup(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.api.auth.send_email", mock_send_email)
    response = client.post("api/auth/register", json=user_data)
    assert response.status_code == status.HTTP_201_CREATED, response.text
    data = response.json()
    assert data["username"] == user_data["username"]
    assert data["email"] == user_data["email"]
    assert "hashed_password" not in data
    assert "avatar" in data


def test_repeat_signup(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.api.auth.send_email", mock_send_email)
    response = client.post("api/auth/register", json=user_data)
    assert response.status_code == status.HTTP_409_CONFLICT, response.text
    data = response.json()
    assert data["detail"] == messages.USER_EMAIL_EXISTS


def test_not_confirmed_login(client):
    response = client.post(
        "api/auth/login",
        json={
            "email": user_data.get("email"),
            "password": user_data.get("password"),
        },
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED, response.text
    data = response.json()
    assert data["detail"] == messages.USER_NOT_CONFIRMED


@pytest.mark.asyncio
async def test_login(client):
    async with TestingSessionLocal() as session:
        current_user = await session.execute(
            select(User).where(User.email == user_data.get("email"))
        )
        current_user = current_user.scalar_one_or_none()
        if current_user:
            current_user.confirmed = True
            await session.commit()

    response = client.post(
        "api/auth/login",
        json={
            "email": user_data.get("email"),
            "password": user_data.get("password"),
        },
    )
    assert response.status_code == status.HTTP_201_CREATED, response.text
    data = response.json()
    assert "access_token" in data
    assert "token_type" in data
    assert data["token_type"] == "bearer", f'token_type should be {data["token_type"]}'


def test_wrong_password_login(client):
    response = client.post(
        "api/auth/login",
        json={"email": user_data.get("email"), "password": "password"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED, response.text
    data = response.json()
    assert data["detail"] == messages.USER_NOT_FOUND


def test_wrong_email_login(client):
    response = client.post(
        "api/auth/login",
        json={"email": "wrong@email.dis", "password": user_data.get("password")},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED, response.text
    data = response.json()
    assert data["detail"] == messages.USER_NOT_FOUND


def test_validation_error_login(client):
    response = client.post(
        "api/auth/login", json={"password": user_data.get("password")}
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY, response.text
    data = response.json()
    assert "detail" in data


def test_request_email(client):
    response = client.post(
        "api/auth/request_email",
        json={"email": user_data.get("email")},
    )
    assert response.status_code == status.HTTP_201_CREATED, response.text
    data = response.json()
    assert data["message"] == messages.USER_EMAIL_CONFIRMED_ALREADY


def test_reset_password_user_not_found(client, monkeypatch):
    mock_get_user_by_email = Mock(return_value=None)
    monkeypatch.setattr(
        "src.services.users.UserService.get_user_by_email", mock_get_user_by_email
    )

    response = client.post(
        "api/auth/reset_password",
        json={"email": "nonexistent@example.com"},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.text
    data = response.json()
    assert data["detail"] == messages.USER_NOT_FOUND


@pytest.mark.asyncio
async def test_register_existing_email(client):
    async with TestingSessionLocal() as session:
        current_user = await session.execute(
            select(User).where(User.email == user_data.get("email"))
        )
        current_user = current_user.scalar_one_or_none()
        if current_user:
            current_user.confirmed = True
            await session.commit()

    response = client.post(
        "api/auth/register",
        json={
            "username": user_data.get("username"),
            "email": user_data.get("email"),
            "password": user_data.get("password"),
            "role": user_data.get("role"),
        },
    )
    if user_data.get("email"):
        assert response.status_code == status.HTTP_409_CONFLICT, response.text
        data = response.json()
        assert data["detail"] == messages.USER_EMAIL_EXISTS


def test_register_existing_username(client, monkeypatch):
    mock_get_user_by_username = Mock(return_value=None)
    monkeypatch.setattr(
        "src.services.users.UserService.get_user_by_username", mock_get_user_by_username
    )

    response = client.post(
        "api/auth/register",
        json={
            "username": user_data.get("username"),
            "email": user_data.get("email"),
            "password": user_data.get("password"),
            "role": user_data.get("role"),
        },
    )
    assert response.status_code == status.HTTP_409_CONFLICT, response.text
    data = response.json()
    assert data["detail"] == messages.USER_EMAIL_EXISTS


def test_get_current_user_role_admin():
    result = get_current_user_role(admin_data)
    assert (
        result.get("role") == UserRole.ADMIN.value
    ), f"Expected role ADMIN, got {result.get("role")}"


def test_get_current_user_role_non_admin():
    with pytest.raises(HTTPException) as exc_info:
        get_current_user_role(user_data)

    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
    assert exc_info.value.detail == messages.ACCESS_DENIED
