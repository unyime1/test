"""Test setup module."""

import logging
import asyncio

import pytest
import redis
import requests
import pytest_asyncio
from fastapi import FastAPI
from asgi_lifespan import LifespanManager
from httpx import AsyncClient

from server import get_application
from models.user import Users
from library.security.hash import hash_service
from library.utils import email  # noqa


logger = logging.getLogger(__name__)


@pytest.fixture(scope="module")
def app() -> FastAPI:
    """get a reference to the application"""
    app = get_application()
    return app


@pytest_asyncio.fixture(scope="module", autouse=True)
async def client(app) -> AsyncClient:
    """Instantiate test client."""
    async with LifespanManager(app):
        async with AsyncClient(
            app=app,
            base_url="http://testserver",
            headers={"Content-Type": "application/json"},
        ) as client:
            yield client


@pytest.fixture(scope="session")
def event_loop(request):
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="class", autouse=True)
async def clean_database():
    """Clean test database at the end of each test class."""
    yield
    await Users.all().delete()


@pytest_asyncio.fixture()
async def test_user():
    password = "passWord23&"
    user_email = "support@eelclip.com"

    user = await Users.get_or_none(email=user_email)
    if user:
        return user

    return await Users.create(
        email=user_email,
        first_name="Eelclip",
        last_name="Support",
        password_hash=await hash_service.get_hash(password),
    )


@pytest.fixture(autouse=True)
def clean_all_db():
    """Clean the whole redis db before each test class"""
    r = redis.Redis(host="redis", port=6379)
    r.flushall()


class MockNameSearchResponse:
    status_code = 200

    @staticmethod
    def json():
        return {"message": "mocked"}


@pytest.fixture()
def mock_email_sending(monkeypatch):
    def mock_post(*args, **kwargs):
        return MockNameSearchResponse()

    monkeypatch.setattr(requests, "post", mock_post)
