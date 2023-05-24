import pytest
import redis
from fastapi import FastAPI, status
from httpx import AsyncClient

from models.user import Users
from library.security.jwt import jwt_manager
from library.security.otp import otp_manager
from library.security.hash import hash_service
from library.schemas.auth import AuthResponse


pytestmark = pytest.mark.asyncio


class TestLogin:
    async def test_login_unverified_email(
        self, app: FastAPI, client: AsyncClient, test_user: Users
    ) -> None:
        """Test Login."""
        password = "passWord23&"

        res = await client.post(
            app.url_path_for("auth:login"),
            json=dict(email=test_user.email, password=password),
        )
        assert res.status_code == status.HTTP_401_UNAUTHORIZED
        assert (
            res.json().get("detail")
            == "Your account is unverified. Please verify to continue."
        )

    async def test_login(
        self, app: FastAPI, client: AsyncClient, test_user: Users
    ) -> None:
        """Test Login."""
        password = "passWord23&"
        test_user.is_verified = True
        await test_user.save()

        res = await client.post(
            app.url_path_for("auth:login"),
            json=dict(email=test_user.email, password=password),
        )
        assert res.status_code == status.HTTP_200_OK
        data = AuthResponse(**res.json())
        assert data.user.id == test_user.id
        assert data.user.email == test_user.email
        assert data.user.first_name == test_user.first_name
        assert data.user.last_name == test_user.last_name
        assert data.access_token

        print(data.access_token)

        token_data = await jwt_manager.decode_access_token(
            access_token=data.access_token
        )
        assert token_data
        assert token_data.user_id == str(test_user.id)
        assert token_data.scopes[0] == test_user.user_class

    async def test_login_wrong_password(
        self, app: FastAPI, client: AsyncClient, test_user: Users
    ) -> None:
        """Test Login."""
        password = "passWord23&-wrong"

        res = await client.post(
            app.url_path_for("auth:login"),
            json=dict(email=test_user.email, password=password),
        )
        assert res.status_code == status.HTTP_401_UNAUTHORIZED
        assert (
            res.json().get("detail") == "Your email or password is incorrect."
        )

    async def test_login_wrong_email(
        self, app: FastAPI, client: AsyncClient, test_user: Users
    ) -> None:
        """Test Login."""
        password = "passWord23&"

        res = await client.post(
            app.url_path_for("auth:login"),
            json=dict(email="fake@test.com", password=password),
        )
        assert res.status_code == status.HTTP_401_UNAUTHORIZED
        assert (
            res.json().get("detail") == "Your email or password is incorrect."
        )


class TestRequestReset:
    redis_db = redis.Redis(host="redis", port=6379, db=1)

    async def test_request_reset(
        self,
        app: FastAPI,
        client: AsyncClient,
        test_user: Users,
        mock_email_sending,
    ) -> None:
        res = await client.post(
            app.url_path_for("auth:request_password_reset"),
            json=dict(email=test_user.email),
        )
        assert res.status_code == status.HTTP_200_OK
        assert (
            res.json().get("message")
            == "We will send you an email if you have an account with us."
        )
        data_keys = self.redis_db.keys()
        assert len(data_keys) == 1

    async def test_request_reset_with_wrong_email(
        self,
        app: FastAPI,
        client: AsyncClient,
        test_user: Users,
        mock_email_sending,
    ) -> None:
        res = await client.post(
            app.url_path_for("auth:request_password_reset"),
            json=dict(email="wrong@eelclip.com"),
        )
        assert res.status_code == status.HTTP_200_OK
        assert (
            res.json().get("message")
            == "We will send you an email if you have an account with us."
        )
        data_keys = self.redis_db.keys()
        assert len(data_keys) == 0


class TestConfirmPasswordReset:
    redis_db = redis.Redis(host="redis", port=6379, db=1)

    async def test_confirm_reset(
        self, app: FastAPI, client: AsyncClient, test_user: Users
    ) -> None:
        """Confirm password reset."""
        otp = otp_manager.create_otp(user_id=str(test_user.id))
        password = "passWord123&@#"
        res = await client.post(
            app.url_path_for("auth:confirm_password_reset"),
            json=dict(otp=otp, new_password=password),
        )
        assert res.status_code == status.HTTP_200_OK
        user = await Users.get(id=test_user.id)
        assert await hash_service.verify_hash(
            string=password, hash=user.password_hash
        )

        data = AuthResponse(**res.json())
        assert data.user.id == test_user.id
        assert data.user.email == test_user.email
        assert data.user.first_name == test_user.first_name
        assert data.user.last_name == test_user.last_name
        assert data.access_token

        token_data = await jwt_manager.decode_access_token(
            access_token=data.access_token
        )
        assert token_data
        assert token_data.user_id == str(test_user.id)
        assert token_data.scopes[0] == test_user.user_class

        data_keys = self.redis_db.keys()
        assert len(data_keys) == 0

    async def test_confirm_reset_wrong_otp(
        self, app: FastAPI, client: AsyncClient, test_user: Users
    ) -> None:
        """Confirm password reset."""
        otp_manager.create_otp(user_id=str(test_user.id))
        password = "passWord123&@#"
        res = await client.post(
            app.url_path_for("auth:confirm_password_reset"),
            json=dict(otp="fake_otp", new_password=password),
        )
        assert res.status_code == status.HTTP_401_UNAUTHORIZED
        assert (
            res.json().get("detail")
            == "Your token is either expired or invalid."
        )

    async def test_confirm_reset_weak_password(
        self, app: FastAPI, client: AsyncClient, test_user: Users
    ) -> None:
        """Confirm password reset."""
        otp = otp_manager.create_otp(user_id=str(test_user.id))
        password = "passWord123"
        res = await client.post(
            app.url_path_for("auth:confirm_password_reset"),
            json=dict(otp=otp, new_password=password),
        )
        assert res.status_code == status.HTTP_400_BAD_REQUEST
        assert (
            res.json().get("detail")
            == "Your password should contain atleast 1 uppercase, 1 lowercase, 1 digit, and 1 special character."  # noqa
        )
