import pytest
from datetime import date, timedelta
from pydantic import ValidationError
from src.schemas.contacts import ContactBase
from src.conf import messages


def test_valid_contact():
    contact = ContactBase(
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        phone_number="1234567890",
        birthday=date(2000, 1, 1),
        additional_data="Some notes",
    )
    assert contact.first_name == "John"


def test_invalid_future_birthday():
    with pytest.raises(ValidationError) as exc:
        ContactBase(
            first_name="Jane",
            last_name="Doe",
            email="jane.doe@example.com",
            phone_number="9876543210",
            birthday=date.today() + timedelta(days=1),
        )
    assert messages.INVALID_BIRTHDAY in str(exc.value)


def test_invalid_phone_number():
    with pytest.raises(ValidationError) as exc:
        ContactBase(
            first_name="Alice",
            last_name="Smith",
            email="alice.smith@example.com",
            phone_number="abcd1234",
            birthday=date(1990, 5, 15),
        )
    assert messages.INVALID_PHONE_NUMBER in str(exc.value)
