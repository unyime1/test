import re

from fastapi import APIRouter, status, HTTPException, Body
from jinja2 import Environment, FileSystemLoader
from pydantic import EmailStr

from library.security.jwt import jwt_manager
from library.security.hash import hash_service
from library.security.otp import otp_manager
from models.user import Users
from library.schemas.auth import (
    LoginSchema,
    AuthResponse,
    TokenData,
    ConfirmPasswordReset,
)
from library.schemas.shared import StatusResponse
from library.utils.email import send_email


router = APIRouter(prefix="/auth", tags=["Authentication"])
file_loader = FileSystemLoader("./templates")
env = Environment(loader=file_loader)


@router.post(
    "/login/",
    name="auth:login",
    response_model=AuthResponse,
    status_code=status.HTTP_200_OK,
)
async def login(data: LoginSchema):
    """Login user."""
    login_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Your email or password is incorrect.",
    )

    user = await Users.get_or_none(email__iexact=data.email)
    if not user:
        raise login_exception

    is_valid_password = await hash_service.verify_hash(
        string=data.password, hash=user.password_hash
    )
    if not is_valid_password:
        raise login_exception

    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Your account is unverified. Please verify to continue.",
        )

    data = TokenData(user_id=str(user.id), scopes=[user.user_class])
    access_token = await jwt_manager.create_access_token(token_data=data)
    return AuthResponse(user=user, access_token=access_token)


@router.post(
    "/request-password-reset/",
    name="auth:request_password_reset",
    response_model=StatusResponse,
    status_code=status.HTTP_200_OK,
)
async def request_reset(email: EmailStr = Body(..., embed=True)):
    """Request password reset."""
    user = await Users.get_or_none(email__iexact=email)
    if not user:
        return StatusResponse(
            message="We will send you an email if you have an account with us."
        )

    # Send OTP.
    otp = otp_manager.create_otp(user_id=str(user.id))

    template = env.get_template("password_reset.html")
    html = template.render(otp=otp, first_name=user.first_name)
    await send_email(
        to_address=[user.email],
        subject="Password Reset Notification",
        body=html,
        name=user.first_name,
    )
    return StatusResponse(
        message="We will send you an email if you have an account with us."
    )


@router.post(
    "/confirm-password-reset/",
    name="auth:confirm_password_reset",
    response_model=AuthResponse,
    status_code=status.HTTP_200_OK,
)
async def confirm_password_reset(data: ConfirmPasswordReset):
    """Confirm password reset."""

    # Validate otp.
    user_id = otp_manager.validate_user_otp(otp=data.otp)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Your token is either expired or invalid.",
        )

    # Validate password.
    pattern = re.compile(r"(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&_-])")
    if not pattern.search(data.new_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Your password should contain atleast 1 uppercase, 1 lowercase, 1 digit, and 1 special character.",  # noqa
        )

    user = await Users.get(id=user_id)
    user.password_hash = await hash_service.get_hash(string=data.new_password)
    user.is_verified = True
    await user.save()

    # Create access_token.
    data = TokenData(user_id=str(user.id), scopes=[user.user_class])
    access_token = await jwt_manager.create_access_token(token_data=data)

    return AuthResponse(user=user, access_token=access_token)
