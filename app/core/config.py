"""
Private License (fitcharge)

This script is privately licensed and confidential. It is not intended for
public distribution or use without explicit permission from the owner.

All rights reserved (c) 2025.
"""

__author__ = "Premnath Palanichamy, Karthikeyan Kabilan"
__collaborators__ = (
    "Premnath Palanichamy <creativepremnath@gmail.com>, "
    "Karthikeyan Kabilan <karthik.codes.dev@gmail.com>"
)
__copyright__ = "Copyright 2024, Fitcharge"
__license__ = "Refer Terms and Conditions"
__version__ = "1.0"
__maintainer__ = "Premnath Palanichamy"
__status__ = "Development"
__desc__ = "Fitcharge configuration file"


from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field, ConfigDict


class Settings(BaseSettings):
    """
    Application configuration container
    Values load automatically from environment variables or a `.env` file.
    """

    # Database
    database_type: str = Field(..., description="Database type")
    database_user: str = Field(..., description="Database user")
    database_password: str = Field(..., description="Database password")
    database_host: str = Field(..., description="Database host")
    database_port: int = Field(..., description="Database port")
    database_name: str = Field(..., description="Database name")

    # Secrets
    secret_key: str = Field(..., description="Secret key")
    debug: bool = Field(..., description="Debug mode")

    # Email
    email_host: str = Field(..., description="Email host")
    email_port: int = Field(..., description="Email port")
    email_user: str = Field(..., description="Email user")
    email_password: str = Field(..., description="Email password")

    # Redis
    redis_url: str = Field(..., description="Redis URL")

    # Logs
    logpath: str = Field(..., description="Log path")
    logfile: str = Field(..., description="Log file")
    mode: str = Field(..., description="Application mode")
    version: str = Field(..., description="Application version")

    # JWT
    algorithm: str = Field(..., description="JWT algorithm")
    access_token_expire_minutes: int = Field(..., description="Access token expiry (minutes)")
    refresh_token_expire_days: int = Field(..., description="Refresh token expiry (days)")

    # App
    application_url: str = Field(..., description="Application base URL")

    # Encryption Key
    key: str = Field(..., description="Encryption key")

    test_database: str = Field(..., description="Test DB")

    # Oauth2 SSO
    client_id: str = Field(..., description="SSO client ID")
    client_secret: str = Field(..., description="SSO client secret")

    # Pydantic v2 config
    model_config = ConfigDict(
        env_file=str(Path(__file__).parent.parent.parent / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()
