from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from jwt.exceptions import PyJWTError

from app.core.database import get_database
from app.core.security import decode_access_token
from app.schemas.auth import UserResponse

security_scheme = HTTPBearer(auto_error=True)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
) -> UserResponse:
    """
    Dependency that validates the Bearer JWT token, extracts user identity,
    and returns authoritative user information from MongoDB.
    """
    token = credentials.credentials

    try:
        payload = decode_access_token(token)
        user_id: str = payload.get("userId")
        lab_id: str = payload.get("labId")
        role: str = payload.get("role")

        if not user_id or not lab_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication token is missing required claims.",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token is invalid or has expired.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    import time
    from pymongo.errors import AutoReconnect

    database = get_database()
    user = None
    for attempt in range(3):
        try:
            user = database.users.find_one({"userId": user_id})
            break
        except AutoReconnect:
            if attempt == 2:
                raise
            time.sleep(0.2)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User associated with token not found.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.get("isActive", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive.",
        )

    return UserResponse(
        userId=user["userId"],
        labId=user["labId"],
        labName=user.get("labName", ""),
        name=user.get("name", ""),
        email=user.get("email", ""),
        role=user.get("role", role or "admin"),
    )
