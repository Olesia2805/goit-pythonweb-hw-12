from pathlib import Path

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType  # type: ignore
from fastapi_mail.errors import ConnectionErrors  # type: ignore
from pydantic import EmailStr  # type: ignore

from src.services.auth import create_email_token
from src.configuration.config import settings

conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
    MAIL_STARTTLS=settings.MAIL_STARTTLS,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    USE_CREDENTIALS=settings.USE_CREDENTIALS,
    VALIDATE_CERTS=settings.VALIDATE_CERTS,
    TEMPLATE_FOLDER=Path(__file__).parent / "templates",
)


async def send_email(email: EmailStr, username: str, host: str, type: str):
    """
    Send an email for verification or password reset.

    Args:
        email (EmailStr): The recipient's email address.
        username (str): The recipient's username.
        host (str): The host URL.
        type (str): The type of email to send ("verify" or "reset").

    Raises:
        ConnectionErrors: If there is an error sending the email.
    """
    settings = {
        "verify": {
            "subject": "Confirm your email",
            "template": "verify_email.html",
        },
        "reset": {
            "subject": "Reset",
            "template": "reset_password.html",
        },
    }
    try:
        token_verification = create_email_token({"sub": email})
        message = MessageSchema(
            subject=settings[type]["subject"],
            recipients=[email],
            template_body={
                "host": host,
                "username": username,
                "token": token_verification,
            },
            subtype=MessageType.html,
        )

        fm = FastMail(conf)
        await fm.send_message(message, template_name=settings[type]["template"])
    except ConnectionErrors as err:
        print(err)
