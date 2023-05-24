"""
This module handles security related features of authentication service.
"""
from datetime import datetime, timedelta, timezone

from jose import jwt
from jose.exceptions import ExpiredSignatureError, JWTError
from fastapi import HTTPException, status
from pydantic import ValidationError

from config import (
    JWT_ALGORITHM,
    ACCESS_TOKEN_EXPIRE_SECONDS,
)
from library.schemas.auth import TokenData
from library.utils.parameters import get_ssm_parameters


class JWTManager:
    parameters = get_ssm_parameters()

    async def create_access_token(
        self,
        token_data: TokenData,
        secret_key: str = parameters["app_secret_key"],
        expires_in: int = ACCESS_TOKEN_EXPIRE_SECONDS,
    ) -> str:
        """Create an access token for user."""
        to_encode = token_data.dict()
        expire = datetime.now(timezone.utc) + timedelta(seconds=expires_in)
        to_encode.update({"exp": expire.timestamp()})
        encoded_jwt = jwt.encode(
            to_encode, secret_key, algorithm=JWT_ALGORITHM
        )
        return encoded_jwt

    async def decode_access_token(
        self, access_token: str, secret_key: str = parameters["app_secret_key"]
    ) -> TokenData:
        """Check that submitted token is valid."""
        try:
            decoded_token = jwt.decode(
                access_token,
                str(secret_key),
                algorithms=[JWT_ALGORITHM],
            )
            payload = TokenData(**decoded_token)
        except ExpiredSignatureError as e:  # noqa
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Your token has expired.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except (JWTError, ValidationError):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token credentials. Please login.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return payload


jwt_manager = JWTManager()
