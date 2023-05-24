"""
This module handles app startup tasks
"""

from typing import Callable
from fastapi import FastAPI
from database.database import init_db


def create_start_app_handler(app: FastAPI) -> Callable:
    async def start_app() -> None:
        await init_db(app)

    return start_app
