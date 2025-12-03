"""
Private License (fitcharge)

This script is privately licensed and confidential. It is not intended for
public distribution or use without explicit permission from the owner.

All rights reserved (c) 2025.
"""

__author__ = "Premnath Palanichamy, Karthikeyan Kabilan"
__collaborators__ = "Premnath Palanichamy <creativepremnath@gmail.com>, Karthikeyan Kabilan <karthik.codes.dev@gmail.com>"
__copyright__ = "Copyright 2024, fitcharge"
__license__ = "Refer Terms and Conditions"
__version__ = "1.0"
__maintainer__ = "Premnath Palanichamy"
__status__ = "Development"
__desc__ = "Fitcharge configuration file"


f"""
Private License (fitcharge)
...
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from pathlib import Path


class Settings(BaseSettings):
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
    mode: str = Field(..., description="Mode")
    version: str = Field(..., description="Version")

    # JWT
    algorithm: str = Field(..., description="JWT algorithm")
    access_token_expire_minutes: int = Field(..., description="Access token expire minutes")
    refresh_token_expire_days: int = Field(..., description="Refresh token expire days")

    # App
    application_url: str = Field(..., description="Application URL")

    # Encryption Key
    key: str = Field(..., description="Encryption key")

    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).parent.parent.parent / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False
    )


settings = Settings()
