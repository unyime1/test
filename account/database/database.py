"""
    This module handles database setup
"""
import logging
from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise
from config import (
    POSTGRES_URL,
    POSTGRES_USER,
    POSTGRES_PASSWORD,
    POSTGRES_HOST,
    POSTGRES_PORT,
    POSTGRES_DB,
)

logger = logging.getLogger(__name__)

MODELS = ["models", "aerich.models"]


TORTOISE_ORM = {
    "connections": {
        "default": {
            "engine": "tortoise.backends.asyncpg",
            "credentials": {
                "host": f"{POSTGRES_HOST}",
                "port": f"{POSTGRES_PORT}",
                "user": f"{POSTGRES_USER}",
                "password": f"{POSTGRES_PASSWORD}",
                "database": f"{POSTGRES_DB}",
            },
        },
    },
    "apps": {
        "models": {
            "models": MODELS,
            "default_connection": "default",
        }
    },
}


async def init_db(app: FastAPI) -> None:
    try:
        register_tortoise(
            app,
            db_url=POSTGRES_URL,
            modules={"models": MODELS},
            generate_schemas=True,
            add_exception_handlers=True,
        )
        logger.warning("--- DB CONNECTION WAS SUCCESSFUL ---")
    except Exception as e:
        logger.warning("--- DB CONNECTION ERROR ---")
        logger.warning(e)
        logger.warning("--- DB CONNECTION ERROR ---")
