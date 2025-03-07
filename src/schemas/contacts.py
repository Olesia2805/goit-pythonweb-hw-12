from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict, EmailStr, field_validator  # type: ignore

from src.configuration import messages


class ContactBase(BaseModel):
    first_name: str = Field(max_length=50, min_length=2)
    last_name: str = Field(max_length=50, min_length=2)
    email: EmailStr
    phone_number: str = Field(max_length=20, min_length=6)
    birthday: date
    additional_data: Optional[str] = Field(max_length=150)

    @field_validator("birthday")
    def validate_birthday(cls, v):
        """
        Validates that the birthday is not in the future.

        Args:
            v (date): The birthday to validate.

        Raises:
            ValueError: If the birthday is in the future.

        Returns:
            date: The validated birthday.
        """
        if v > date.today():
            raise ValueError(messages.INVALID_BIRTHDAY)
        return v

    @field_validator("phone_number")
    def validate_phone_number(cls, v):
        """
        Validates that the phone number contains only digits.

        Args:
            v (str): The phone number to validate.

        Raises:
            ValueError: If the phone number contains non-digit characters.

        Returns:
            str: The validated phone number.
        """
        if not v.isdigit():
            raise ValueError(messages.INVALID_PHONE_NUMBER)
        return v


class ContactResponse(ContactBase):
    id: int
    created_at: datetime | None
    updated_at: Optional[datetime] | None

    model_config = ConfigDict(from_attributes=True)


class ContactBirthdayRequest(BaseModel):
    days: int
