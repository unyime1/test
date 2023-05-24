import pytest
import redis
from fastapi import FastAPI, status
from httpx import AsyncClient

from library.schemas.shared import UserPublic
from models.user import Users
from library.security.jwt import jwt_manager
from library.security.otp import otp_manager
from library.schemas.auth import AuthResponse


pytestmark = pytest.mark.asyncio


class TestRegistration:
    async def test_users_can_register_successfully(
        self, app: FastAPI, client: AsyncClient, mock_email_sending
    ) -> None:
        redis_db = redis.Redis(host="redis", port=6379, db=1)
        user = {
            "first_name": "Unyime",
            "last_name": "Etim",
            "email": "support@eelclip.com",
            "password": "passWord23&",
        }
        data_keys = redis_db.keys()
        assert len(data_keys) == 0

        res = await client.post(
            app.url_path_for("register:user_register"), json=user
        )
        assert res.status_code == status.HTTP_201_CREATED
        data = UserPublic(**res.json())

        data_keys = redis_db.keys()
        assert len(data_keys) == 1

        for key in data_keys:
            assert redis_db.get(key).decode("utf-8") == str(data.id)

        user = await Users.get_or_none(email=user.get("email"))
        assert user
        assert user.first_name == data.first_name
        assert user.last_name == data.last_name
        assert user.password_hash
        assert user.is_verified is False

    async def test_register_with_weak_password(
        self, app: FastAPI, client: AsyncClient, mock_email_sending
    ) -> None:
        """Test that users can register accounts."""
        user = {
            "first_name": "Unyime",
            "last_name": "Etim",
            "email": "support@eelclip.com",
            "password": "passkshdjyr",
        }

        res = await client.post(
            app.url_path_for("register:user_register"), json=user
        )
        assert res.status_code == status.HTTP_400_BAD_REQUEST
        detail = "Your password should contain atleast 1 uppercase, 1 lowercase, 1 digit, and 1 special character."  # noqa
        assert res.json().get("detail") == detail

    async def test_register_with_existing_email(
        self, app: FastAPI, client: AsyncClient, mock_email_sending
    ) -> None:
        """Test that users can register accounts."""
        user = {
            "first_name": "Unyime",
            "last_name": "Etim",
            "email": "support@eelclip.com",
            "password": "passWord23&",
        }

        res = await client.post(
            app.url_path_for("register:user_register"), json=user
        )
        assert res.status_code == status.HTTP_400_BAD_REQUEST
        detail = "This user already exists. Please login instead."
        assert res.json().get("detail") == detail

    async def test_that_registration_email_is_case_insensitive(
        self, app: FastAPI, client: AsyncClient, mock_email_sending
    ) -> None:
        """Test that users can register accounts."""
        user = {
            "first_name": "Unyime",
            "last_name": "Etim",
            "email": "supPort@eelClip.cOm",
            "password": "passWord23&",
        }

        res = await client.post(
            app.url_path_for("register:user_register"), json=user
        )
        assert res.status_code == status.HTTP_400_BAD_REQUEST
        detail = "This user already exists. Please login instead."
        assert res.json().get("detail") == detail


class TestResendVerification:
    email = "support@eelclip.com"

    async def test_resend_successful(
        self, app: FastAPI, client: AsyncClient, mock_email_sending
    ) -> None:
        user = {
            "first_name": "Unyime",
            "last_name": "Etim",
            "email": self.email,
            "password": "passWord23&",
        }

        res = await client.post(
            app.url_path_for("register:user_register"), json=user
        )
        assert res.status_code == status.HTTP_201_CREATED

        res = await client.post(
            app.url_path_for("register:resend_verification_link"),
            json=dict(email=self.email),
        )
        assert res.status_code == status.HTTP_200_OK
        assert res.json().get("message") == "Verification link sent."

    async def test_resend_if_account_does_not_exist(
        self, app: FastAPI, client: AsyncClient, mock_email_sending
    ):
        res = await client.post(
            app.url_path_for("register:resend_verification_link"),
            json=dict(email="test@eelclip.com"),
        )
        assert res.status_code == status.HTTP_404_NOT_FOUND
        assert res.json().get("detail") == "This user does not exist."

    async def test_resend_if_account_is_already_verified(
        self, app: FastAPI, client: AsyncClient, mock_email_sending
    ):
        user = await Users.get(email__iexact=self.email)
        user.is_verified = True
        await user.save()

        res = await client.post(
            app.url_path_for("register:resend_verification_link"),
            json=dict(email=self.email),
        )
        assert res.status_code == status.HTTP_400_BAD_REQUEST
        assert res.json().get("detail") == "This account is already verified."


class TestVerifyAccount:
    async def test_verify_account_if_token_is_invalid(
        self, app: FastAPI, client: AsyncClient, test_user: Users
    ) -> None:
        """Test account verification."""
        redis_db = redis.Redis(host="redis", port=6379, db=1)
        res = await client.post(
            app.url_path_for("register:verify_account"),
            json=dict(otp="wrong_otp"),
        )
        assert res.status_code == status.HTTP_401_UNAUTHORIZED
        assert (
            res.json().get("detail")
            == "Your token is either expired or invalid."
        )

        data_keys = redis_db.keys()
        assert len(data_keys) == 0

    async def test_verify_account(
        self, app: FastAPI, client: AsyncClient, test_user: Users
    ) -> None:
        """Test account verification."""
        redis_db = redis.Redis(host="redis", port=6379, db=1)
        assert test_user.is_verified is False

        otp = otp_manager.create_otp(user_id=str(test_user.id))
        res = await client.post(
            app.url_path_for("register:verify_account"),
            json=dict(otp=otp),
        )
        assert res.status_code == status.HTTP_200_OK
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

        # Check that user is verified.
        user = await Users.get(id=test_user.id)
        assert user.is_verified

        # Check that otp is deleted.
        data_keys = redis_db.keys()
        assert len(data_keys) == 0
