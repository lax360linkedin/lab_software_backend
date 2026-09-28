import logging
import uuid
from datetime import datetime, timezone
from fastapi import HTTPException, status
from pymongo.errors import DuplicateKeyError

from app.core.database import get_database
from app.core.security import hash_password, verify_password, create_access_token
from app.core.roles import UserRole
from app.schemas.auth import (
    SignupRequest,
    SignupResponse,
    LoginRequest,
    LoginResponse,
    UserResponse,
)

logger = logging.getLogger("uvicorn.error")


class AuthService:
    @staticmethod
    def signup_laboratory(data: SignupRequest) -> SignupResponse:
        database = get_database()
        normalized_email = data.email.strip().lower()

        # Check whether email already exists
        existing_user = database.users.find_one({"email": normalized_email})
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email address is already registered.",
            )

        now_iso = datetime.now(timezone.utc).isoformat()
        lab_id = f"LAB-{uuid.uuid4().hex[:8].upper()}"
        user_id = f"USR-{uuid.uuid4().hex[:8].upper()}"

        lab_document = {
            "labId": lab_id,
            "labName": data.labName.strip(),
            "phone": data.phone.strip(),
            "address": data.address.strip(),
            "createdAt": now_iso,
        }

        # Insert lab document
        try:
            database.labs.insert_one(lab_document)
        except Exception as exc:
            logger.error("Error creating lab document: %s", exc)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to initialize laboratory account. Please try again.",
            )

        # Hash password and create admin user document
        hashed_password = hash_password(data.password)
        user_document = {
            "userId": user_id,
            "labId": lab_id,
            "labName": data.labName.strip(),
            "name": data.adminName.strip(),
            "email": normalized_email,
            "phone": data.phone.strip(),
            "passwordHash": hashed_password,
            "role": UserRole.ADMIN.value,
            "isActive": True,
            "createdAt": now_iso,
            "updatedAt": now_iso,
        }

        try:
            database.users.insert_one(user_document)
        except DuplicateKeyError:
            # Rollback orphan lab document if user insertion fails
            database.labs.delete_one({"labId": lab_id})
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email address is already registered.",
            )
        except Exception as exc:
            # Rollback orphan lab document
            database.labs.delete_one({"labId": lab_id})
            logger.error("Error creating admin user document: %s", exc)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user account. Please try again.",
            )

        return SignupResponse(message="Laboratory account created successfully")

    @staticmethod
    def login_user(data: LoginRequest) -> LoginResponse:
        database = get_database()
        normalized_email = data.email.strip().lower()

        user = database.users.find_one({"email": normalized_email})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not verify_password(data.password, user.get("passwordHash", "")):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.get("isActive", True):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is inactive. Please contact support.",
            )

        user_role = user.get("role", UserRole.ADMIN.value)
        if user_role not in [r.value for r in UserRole]:
            user_role = UserRole.ADMIN.value

        token_payload = {
            "sub": user["userId"],
            "userId": user["userId"],
            "labId": user["labId"],
            "role": user_role,
        }
        access_token = create_access_token(token_payload)

        return LoginResponse(
            accessToken=access_token,
            tokenType="bearer",
            user=UserResponse(
                userId=user["userId"],
                labId=user["labId"],
                labName=user.get("labName", ""),
                name=user.get("name", ""),
                email=user.get("email", ""),
                role=user_role,
            ),
        )
