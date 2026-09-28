from typing import Sequence, Union
from fastapi import Depends, HTTPException, status
from app.core.roles import UserRole
from app.dependencies.auth import get_current_user
from app.schemas.auth import UserResponse


class RoleChecker:
    """
    Authorization dependency that checks whether the authenticated user has one of the allowed roles.
    Authentication ('Who is the user?') is verified first by get_current_user.
    Authorization ('What is this user allowed to access?') is evaluated here.
    """

    def __init__(self, allowed_roles: Sequence[Union[UserRole, str]]):
        self.allowed_roles = [
            r.value if isinstance(r, UserRole) else str(r) for r in allowed_roles
        ]

    def __call__(
        self,
        current_user: UserResponse = Depends(get_current_user),
    ) -> UserResponse:
        if current_user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to access this resource.",
            )
        return current_user


def require_role(role: Union[UserRole, str]) -> RoleChecker:
    """
    Authorization dependency factory requiring a single specific role.
    Example usage:
        @router.get("/admin-only")
        def route(user: UserResponse = Depends(require_role(UserRole.ADMIN))):
    """
    return RoleChecker([role])


def require_roles(*roles: Union[UserRole, str]) -> RoleChecker:
    """
    Authorization dependency factory requiring any of the specified roles.
    Example usage:
        @router.get("/clinical-route")
        def route(user: UserResponse = Depends(require_roles(UserRole.ADMIN, UserRole.LAB_TECHNICIAN))):
    """
    return RoleChecker(roles)


def get_current_lab_id(
    current_user: UserResponse = Depends(get_current_user),
) -> str:
    """
    Extracts the authenticated laboratory identity (labId) directly from the verified session.
    Prevents cross-laboratory tampering by ensuring backend identity is authoritative.
    """
    return current_user.labId


def ensure_lab_access(resource_lab_id: str, current_user: UserResponse) -> None:
    """
    Enforces multi-tenant data isolation. Ensures that the requested resource
    belongs strictly to the authenticated user's laboratory.
    Raises 403 Forbidden if a tenant boundary violation is detected.
    """
    if current_user.labId != resource_lab_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cross-laboratory access forbidden.",
        )
