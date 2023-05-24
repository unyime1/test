"""
This module handles application configurations
"""
from starlette.config import Config
from starlette.datastructures import Secret

config = Config(".env")

PROJECT_NAME = "eelclip"

TESTING = config("TESTING", cast=bool, default=False)
LIVE = config("LIVE", cast=bool, default=False)

# POSTGRES settings
POSTGRES_USER = config("POSTGRES_USER", cast=Secret)
POSTGRES_PASSWORD = config("POSTGRES_PASSWORD", cast=Secret)
POSTGRES_HOST = config("POSTGRES_HOST", cast=Secret)
POSTGRES_PORT = config("POSTGRES_PORT", cast=Secret)
POSTGRES_DB = config("POSTGRES_DB", cast=str)

POSTGRES_URL = config(
    "POSTGRES_URL",
    default=f"postgres://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}",  # noqa
)  # noqa


JWT_ALGORITHM = config("ALGORITHM", cast=str, default="HS256")
ACCESS_TOKEN_EXPIRE_SECONDS = config(
    "ACCESS_TOKEN_EXPIRE_SECONDS", cast=int, default=604800  # 1 week
)
