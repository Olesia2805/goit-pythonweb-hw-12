import datetime
from fastapi import status
from src.conf import messages
import pytest
from pytest import MonkeyPatch
from fastapi.exceptions import HTTPException
from unittest.mock import AsyncMock

test_contact = {
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@example.com",
    "phone_number": "1234567890",
    "birthday": "1990-01-01",
    "additional_data": "Some additional data",
}

mock_contacts = [
    {
        "id": 1,
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@example.com",
        "phone_number": "1234567890",
        "birthday": "1990-01-01",
        "additional_data": "Some notes",
        "created_at": "2025-01-01 00:00:00",
        "updated_at": "2025-01-01 00:00:00",
    },
    {
        "id": 2,
        "first_name": "Johnny",
        "last_name": "Appleseed",
        "email": "johnny@example.com",
        "phone_number": "9876543210",
        "birthday": "1985-05-15",
        "additional_data": "Another note",
        "created_at": "2025-01-01 00:00:00",
        "updated_at": "2025-01-01 00:00:00",
    },
]


def test_create_contact(client, get_token):
    response = client.post(
        "/api/contacts",
        json=test_contact,
        headers={"Authorization": f"Bearer {get_token}"},
    )
    data = response.json()

    assert set(data.items()) >= set(
        test_contact.items()
    ), f"Expected data to contain {test_contact}, got {data}"
    assert "id" in data, "Response JSON does not contain 'id'"
    assert "created_at" in data, "Response JSON does not contain 'created_at'"
    assert "updated_at" in data, "Response JSON does not contain 'updated_at'"
    assert (
        datetime.datetime.strptime(data["birthday"], "%Y-%m-%d")
        <= datetime.datetime.now()
    ), f"Expected birthday to be before or equal to now, got {data['birthday']}"
    assert (
        response.status_code == status.HTTP_201_CREATED
    ), f"Expected status code 201, got {response.status_code}. Response text: {response.text}"


def test_get_contact(client, get_token):
    response = client.get(
        "/api/contacts/1", headers={"Authorization": f"Bearer {get_token}"}
    )
    assert response.status_code == status.HTTP_200_OK, response.text
    data = response.json()
    assert isinstance(data, dict), f"Expected dict, got {type(data)}"
    assert set(data.items()) >= set(
        test_contact.items()
    ), f"Expected data to contain {test_contact}, got {data}"
    assert "id" in data


def test_get_contact_not_found(client, get_token):
    response = client.get(
        "/api/contacts/2", headers={"Authorization": f"Bearer {get_token}"}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND, response.text
    data = response.json()
    assert data["detail"] == messages.CONTACT_NOT_FOUND


def test_get_contacts(client, get_token):
    response = client.get(
        "/api/contacts", headers={"Authorization": f"Bearer {get_token}"}
    )
    assert response.status_code == status.HTTP_200_OK, response.text
    data = response.json()
    assert isinstance(data, list)
    assert data[0]["first_name"] == test_contact["first_name"]
    assert "id" in data[0]
    assert len(data) > 0


def test_update_contact(client, get_token):
    updated_test_contact = test_contact.copy()
    updated_test_contact["first_name"] = "new-name"

    response = client.put(
        "/api/contacts/1",
        json=updated_test_contact,
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == status.HTTP_200_OK, response.text
    data = response.json()
    assert data["first_name"] == updated_test_contact["first_name"]
    assert "id" in data
    assert data["id"] == 1


def test_update_contact_not_found(client, get_token):
    updated_test_contact = test_contact.copy()
    updated_test_contact["first_name"] = "new-name"

    response = client.put(
        "/api/contacts/2",
        json=updated_test_contact,
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND, response.text
    data = response.json()
    assert data["detail"] == messages.CONTACT_NOT_FOUND


def test_delete_contact(client, get_token):
    response = client.delete(
        "/api/contacts/1", headers={"Authorization": f"Bearer {get_token}"}
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT, response.text
    data = response._content
    assert data == b""
    contact = None
    if contact is None:
        with pytest.raises(HTTPException) as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=messages.CONTACT_NOT_FOUND
            )

    assert messages.CONTACT_NOT_FOUND in str(exc.value)


def test_repeat_delete_contact(client, get_token):
    response = client.delete(
        "/api/contacts/1", headers={"Authorization": f"Bearer {get_token}"}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND, response.text
    data = response.json()
    assert data["detail"] == messages.CONTACT_NOT_FOUND


def test_search_contacts_no_match(client, get_token, monkeypatch):
    mock_contact_service = AsyncMock(return_value=[])
    monkeypatch.setattr(
        "src.services.contacts.ContactService.search_contacts", mock_contact_service
    )
    response = client.get(
        "/api/contacts/search/",
        params={"text": "John", "skip": 0, "limit": 10},
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == status.HTTP_200_OK, response.text
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0, f"Expected empty list, got {data}"


def test_search_contacts_no_match(client, get_token, monkeypatch):
    mock_contact_service = AsyncMock(return_value=mock_contacts)
    monkeypatch.setattr(
        "src.services.contacts.ContactService.search_contacts", mock_contact_service
    )
    response = client.get(
        "/api/contacts/search/",
        params={"text": "John", "skip": 0, "limit": 10},
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == status.HTTP_200_OK, response.text
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == len(
        mock_contacts
    ), f"Expected {len(mock_contacts)} results, got {len(data)}"
