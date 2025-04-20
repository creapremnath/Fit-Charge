"""
Private License (fitcharge)

This script is privately licensed and confidential. It is not intended for
public distribution or use without explicit permission from the owner.

All rights reserved (c) 2025.
"""

__author__        = "Premnath Palanichamy, Karthikeyan Kabilan"
__collaborators__ = "Premnath Palanichamy <creativepremnath@gmail.com>, Karthikeyan Kabilan <karthik.codes.dev@gmail.com>"
__copyright__     = "Copyright 2024, fitcharge"
__license__       = "Refer Terms and Conditions"
__version__       = "1.0"
__maintainer__    = "Premnath Palanichamy"
__status__        = "Development"
__desc__          = "Fitcharge configuration file"


f"""
Private License (fitcharge)
...
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
from urllib.parse import quote

class Settings(BaseSettings):
    # Your fields remain the same...
    database_type: str = Field(..., env="DATABASE_TYPE")
    database_user: str = Field(..., env="DATABASE_USER")
    database_password: str = Field(..., env="DATABASE_PASSWORD")
    database_host: str = Field(..., env="DATABASE_HOST")
    database_port: int = Field(..., env="DATABASE_PORT")
    database_name: str = Field(..., env="DATABASE_NAME")
    secret_key: str = Field(..., env="SECRET_KEY")
    debug: bool = Field(False, env="DEBUG")
    email_host: str = Field(..., env="EMAIL_HOST")
    email_port: int = Field(..., env="EMAIL_PORT")
    email_user: str = Field(..., env="EMAIL_USER")
    email_password: str = Field(..., env="EMAIL_PASSWORD")
    redis_url: str = Field(..., env="REDIS_URL")
    logpath: str = Field(..., env="LOGPATH")
    logfile: str = Field(..., env="LOGFILE")
    mode: str = Field("INFO", env="MODE")
    version: str = Field("1.0.0", env="VERSION")
    algorithm: str = Field("HS256", env="ALGORITHM")
    access_token_expire_minutes: int = Field(30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(1, env="REFRESH_TOKEN_EXPIRE_DAYS")
    application_url: str = Field(..., env="APPLICATION_URL")
    key: str = Field(..., env="KEY")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
