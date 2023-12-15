import secrets
import os
from os.path import join
from typing import List, Any
from pydantic import BaseSettings, HttpUrl, EmailStr, AnyHttpUrl, PostgresDsn, validator
from dotenv import load_dotenv

load_dotenv(override=True)  # loads environment variable


class Settings(BaseSettings):
    API_V1_STR: str = "/v1"
    PROJECT_NAME: str = "Library Management API"
    DESCRIPTION: str = """
    This is a REST API for library managment, developed using Python and FastAPI
    it was created as an excersise 
"""
    PRODUCTION: bool = False
    SECRET_KEY: str = secrets.token_urlsafe(32)

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    ALGORITHM = "HS256"
    AUTH_SCOPES = {
        "users:read": "Reads users",
        "users:write": "Writes user data or can update user data",
        "users:delete": "Can Delete user account",
        "items:read": "Reads items",
        "items:write": "Write or update items in catalogue",
        "items:delete": "Delete items from catalogue",
        "borrow:issue": "Can issue a new borrow request",
        "borrow:return": "Can accept borrow returns",
        "borrow:renew": "Can initiate borrow renew"
    }

    SERVER_NAME: str = "Libra"
    SERVER_HOST: AnyHttpUrl = "http://localhost"
    # BACKEND_CORS_ORIGINS is a JSON-formatted list of origins
    # e.g: '["http://localhost", "http://localhost:4200", "http://localhost:3000", \
    # "http://localhost:8080", "http://local.dockertoolbox.tiangolo.com"]'
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = ["http://localhost", "http://localhost:3000", ]

    # DATABASE CONNECTION VARIABLES
    DB_HOST: str
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str
    DB_URI: PostgresDsn | None

    @validator("DB_URI", pre=True)
    def assemble_db_connection(cls, v: str | None, values: dict[str, Any]):
        if isinstance(v, str):
            return v

        return PostgresDsn.build(
            scheme="postgresql",
            user=values.get("DB_USER"),
            host=values.get("DB_HOST"),
            password=values.get("DB_PASSWORD"),
            path=f"/{values.get("DB_NAME", "")}"
        )

    # SMTP Config Environment Variables
    SMTP_TLS: bool = True
    SMTP_PORT: int = None
    SMTP_HOST: str = None
    SMTP_USER: str = None
    SMTP_PASSWORD: str = None
    EMAILS_FROM_EMAIL: EmailStr = None
    EMAILS_FROM_NAME: str = "Library Admin"
    EMAIL_TEMPLATES_DIR: str = join(os.getcwd(), "app", "utils", "email-templates")

    class Config:
        case_sensitive = True


settings = Settings()
