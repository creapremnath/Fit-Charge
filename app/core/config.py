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

from pydantic_settings import BaseSettings
from pydantic import Field


from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # Database
    database_type: str = Field(..., env="DATABASE_TYPE")
    database_user: str = Field(..., env="DATABASE_USER")
    database_password: str = Field(..., env="DATABASE_PASSWORD")
    database_host: str = Field(..., env="DATABASE_HOST")
    database_port: int = Field(..., env="DATABASE_PORT")
    database_name: str = Field(..., env="DATABASE_NAME")

    # Secrets
    secret_key: str = Field(..., env="SECRET_KEY")
    debug: bool = Field(..., env="DEBUG")

    # Email
    email_host: str = Field(..., env="EMAIL_HOST")
    email_port: int = Field(..., env="EMAIL_PORT")
    email_user: str = Field(..., env="EMAIL_USER")
    email_password: str = Field(..., env="EMAIL_PASSWORD")

    # Redis
    redis_url: str = Field(..., env="REDIS_URL")

    # Logs
    logpath: str = Field(..., env="LOGPATH")
    logfile: str = Field(..., env="LOGFILE")
    mode: str = Field(..., env="MODE")
    version: str = Field(..., env="VERSION")

    # JWT
    algorithm: str = Field(..., env="ALGORITHM")
    access_token_expire_minutes: int = Field(..., env="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(..., env="REFRESH_TOKEN_EXPIRE_DAYS")

    # App
    application_url: str = Field(..., env="APPLICATION_URL")

    # Encryption Key
    key: str = Field(..., env="KEY")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
