from unittest.mock import Mock
from fastapi import status

import pytest
from sqlalchemy import select

from src.database.models import User
from src.conf import messages
from tests.conftest import TestingSessionLocal
from src.services.users import UserService
from src.schemas.users import UserCreate

user_data = {
    "username": "agent007",
    "email": "agent007@gmail.com",
    "password": "12345678",
    "role": "user",
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
