import re

from fastapi import APIRouter, status, HTTPException, Body
from jinja2 import Environment, FileSystemLoader
from pydantic import EmailStr

from library.schemas.shared import UserPublic, StatusResponse
from library.schemas.register import RegisterIn
from library.security.otp import otp_manager
from library.security.jwt import jwt_manager
from library.security.hash import hash_service
from models.user import Users
from library.utils.email import send_email
from library.schemas.auth import AuthResponse
from library.schemas.auth import TokenData


router = APIRouter(prefix="/register", tags=["Register"])
file_loader = FileSystemLoader("./templates")
env = Environment(loader=file_loader)


@router.post(
    "/user-register/",
    name="register:user_register",
    response_model=UserPublic,
    status_code=status.HTTP_201_CREATED,
)
async def register(data: RegisterIn):
    """Register account."""

    # Validate password.
    pattern = re.compile(r"(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&_-])")
    if not pattern.search(data.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Your password should contain atleast 1 uppercase, 1 lowercase, 1 digit, and 1 special character.",  # noqa
        )

    # Confirm that user does not exist.
    user_exists = await Users.filter(email__iexact=data.email).exists()
    if user_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This user already exists. Please login instead.",
        )

    # Create account.
    user = await Users.create(
        email=data.email,
        first_name=data.first_name,
        last_name=data.last_name,
        password_hash=await hash_service.get_hash(string=data.password),
    )

    # Send OTP.
    otp = otp_manager.create_otp(user_id=str(user.id))

    template = env.get_template("email_verification.html")
    html = template.render(otp=otp, first_name=data.first_name)
    await send_email(
        to_address=[data.email],
        subject="Verify Your Account",
        body=html,
        name=user.first_name,
    )

    return user


@router.post(
    "/resend-verification-link/",
    name="register:resend_verification_link",
    response_model=StatusResponse,
    status_code=status.HTTP_200_OK,
)
async def resend_verification(email: EmailStr = Body(..., embed=True)):
    """Resend account verification link."""
    # Confirm that user does not exist.
    user = await Users.get_or_none(email__iexact=email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="This user does not exist.",
        )
    if user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This account is already verified.",
        )

    # Send OTP.
    otp = otp_manager.create_otp(user_id=str(user.id))

    template = env.get_template("email_verification.html")
    html = template.render(otp=otp, first_name=user.first_name)
    await send_email(
        to_address=[email],
        subject="Verify Account",
        body=html,
        name=user.first_name,
    )

    return StatusResponse(message="Verification link sent.")


@router.post(
    "/verify-account/",
    name="register:verify_account",
    response_model=AuthResponse,
    status_code=status.HTTP_200_OK,
)
async def verify_verification(otp: str = Body(..., embed=True)):
    """Verify account."""
    # Validate token.
    user_id = otp_manager.validate_user_otp(otp=otp)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Your token is either expired or invalid.",
        )
    user = await Users.get(id=user_id)
    user.is_verified = True
    await user.save()

    # Create access_token.
    data = TokenData(user_id=str(user.id), scopes=[user.user_class])
    access_token = await jwt_manager.create_access_token(token_data=data)

    return AuthResponse(user=user, access_token=access_token)
