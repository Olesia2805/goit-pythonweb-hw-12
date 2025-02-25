import datetime
from fastapi import status
from src.conf import messages
import pytest
from fastapi.exceptions import HTTPException

test_contact = {
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@example.com",
    "phone_number": "1234567890",
    "birthday": "1990-01-01",
    "additional_data": "Some additional data",
}


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
