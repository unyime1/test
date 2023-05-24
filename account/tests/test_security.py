import pytest
import time
import redis
from fastapi import FastAPI, HTTPException
from passlib.context import CryptContext

from library.security.hash import hash_service
from library.security.jwt import jwt_manager
from library.security.otp import otp_manager
from models.user import Users
from library.schemas.auth import TokenData
from library.utils.random import create_random_code


pytestmark = pytest.mark.asyncio


class TestHash:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    async def test_hash(self, app: FastAPI) -> None:
        """Test string hashing."""
        password = "I love eelclip!"
        hash = await hash_service.get_hash(string=password)

        assert hash
        assert 1 == 1
        assert len(hash) == 60

        assert self.pwd_context.verify(password, hash)
        assert not self.pwd_context.verify("wrong password", hash)

    async def test_verify_hash(
        self,
        app: FastAPI,
    ) -> None:
        """Test string hashing."""
        password = "I love eelclip!"
        hash = self.pwd_context.hash(password)

        assert hash
        assert len(hash) == 60

        assert await hash_service.verify_hash(password, hash)
        assert not await hash_service.verify_hash("wrong password", hash)


class TestJWT:
    async def test_create_access_token(
        self, app: FastAPI, test_user: Users
    ) -> None:
        token_data = TokenData(
            user_id=str(test_user.id), scopes=[test_user.user_class]
        )

        # Encode
        token = await jwt_manager.create_access_token(
            token_data=token_data,
        )
        assert token
        assert "ey" in token

        # Decode.
        data = await jwt_manager.decode_access_token(access_token=token)
        assert data.user_id == str(test_user.id)
        assert data.scopes[0] == test_user.user_class

    async def test_expire(self, app: FastAPI, test_user: Users) -> None:
        token_data = TokenData(
            user_id=str(test_user.id), scopes=[test_user.user_class]
        )

        # Encode
        token = await jwt_manager.create_access_token(
            token_data=token_data, expires_in=1
        )
        assert token
        assert "ey" in token
        time.sleep(2)

        # Decode.
        with pytest.raises(HTTPException):
            data = await jwt_manager.decode_access_token(access_token=token)
            print(data)


class TestOTP:
    redis_db = redis.Redis(host="redis", port=6379, db=1)

    async def test_create_otp(
        self,
        app: FastAPI,
    ) -> None:
        """Test OTP creation."""
        user_id = "fake_code"
        generated_otp = otp_manager.create_otp(user_id=user_id)
        time.sleep(2)
        assert self.redis_db.get(generated_otp) is not None
        assert self.redis_db.get(generated_otp).decode("utf-8") == user_id

    async def test_otp_expires(
        self,
        app: FastAPI,
    ) -> None:
        """Test that OTP expires."""
        user_id = "fake_code"
        generated_otp = otp_manager.create_otp(user_id=user_id, expires=1)
        time.sleep(2)
        assert self.redis_db.get(generated_otp) is None

    async def test_delete_user_otp(
        self,
        app: FastAPI,
    ) -> None:
        """Test OTp deletion."""
        user_id = "fake_code"
        generated_otp = otp_manager.create_otp(user_id=user_id)

        assert self.redis_db.get(generated_otp) is not None
        otp_manager.delete_user_otp(generated_otp)
        assert self.redis_db.get(generated_otp) is None


class TestRandom:
    async def test_create_random_code(
        self,
        app: FastAPI,
    ) -> None:
        """Test create_random_code_utility."""

        codes = []
        for _ in range(0, 1000):
            code = await create_random_code(number=20)
            assert code not in codes
            codes.append(code)
