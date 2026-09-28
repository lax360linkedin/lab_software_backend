from fastapi import APIRouter, Depends, status
from app.schemas.auth import (
    SignupRequest,
    SignupResponse,
    LoginRequest,
    LoginResponse,
    UserResponse,
)
from app.services.auth_service import AuthService
from app.dependencies.auth import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/signup",
    response_model=SignupResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new laboratory account and administrator",
    description="Registers a new medical laboratory along with its primary administrator account.",
)
def signup(data: SignupRequest) -> SignupResponse:
    return AuthService.signup_laboratory(data)


@router.post(
    "/login",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
    summary="User login with JWT authentication",
    description="Authenticates the user and returns an access token along with user details.",
)
def login(data: LoginRequest) -> LoginResponse:
    return AuthService.login_user(data)


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current authenticated user profile",
    description="Returns the profile information of the currently authenticated user extracted from the JWT.",
)
def me(current_user: UserResponse = Depends(get_current_user)) -> UserResponse:
    return current_user
