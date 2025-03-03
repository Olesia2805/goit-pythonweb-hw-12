from pydantic import ConfigDict  # type: ignore
from pydantic_settings import BaseSettings  # type: ignore
from pathlib import Path


class Settings(BaseSettings):
    DB_URL: str = "sqlite+aiosqlite:///./test.db"
    JWT_SECRET: str = "secret"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_SECONDS: int = 3600
    MAIL_USERNAME: str = "username"
    MAIL_PASSWORD: str = "skdnfwRFE4"
    MAIL_FROM: str = "user@example.com"
    MAIL_PORT: int = 465
    MAIL_SERVER: str = "smtp.meta.ua"
    MAIL_FROM_NAME: str = "User"
    MAIL_STARTTLS: bool = False
    MAIL_SSL_TLS: bool = True
    USE_CREDENTIALS: bool = True
    VALIDATE_CERTS: bool = True
    TEMPLATE_FOLDER: Path = Path(__file__).parent.parent / "services" / "templates"

    CLD_NAME: str = "dcoktdgvg"
    CLD_API_KEY: int = 399858629264761
    CLD_API_SECRET: str = "gGFokZ-cpUMuTxBhDqK8cIZpOWY"

    model_config = ConfigDict(
        extra="ignore", env_file=".env", env_file_encoding="utf-8", case_sensitive=True
    )


settings = Settings()
