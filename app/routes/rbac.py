from fastapi import APIRouter, Depends, Query
from app.core.roles import UserRole
from app.dependencies.auth import get_current_user
from app.dependencies.rbac import (
    require_role,
    require_roles,
    ensure_lab_access,
    get_current_lab_id,
)
from app.schemas.auth import UserResponse

router = APIRouter(
    prefix="/rbac",
    tags=["RBAC Verification (Testing Only)"],
)


@router.get(
    "/admin-test",
    summary="[TEST] Admin-only endpoint",
    description="Accessible ONLY by users with role 'admin'. Receptionists and Lab Technicians will receive 403 Forbidden.",
)
def admin_only_test(
    current_user: UserResponse = Depends(require_role(UserRole.ADMIN)),
):
    return {
        "status": "success",
        "message": "Access granted: Administrator authorized.",
        "authorizedRole": current_user.role,
        "userId": current_user.userId,
        "labId": current_user.labId,
    }


@router.get(
    "/receptionist-test",
    summary="[TEST] Receptionist and Admin endpoint",
    description="Accessible by 'admin' and 'receptionist'. Lab Technicians will receive 403 Forbidden.",
)
def receptionist_test(
    current_user: UserResponse = Depends(
        require_roles(UserRole.ADMIN, UserRole.RECEPTIONIST)
    ),
):
    return {
        "status": "success",
        "message": "Access granted: Receptionist/Admin authorized.",
        "authorizedRole": current_user.role,
        "userId": current_user.userId,
        "labId": current_user.labId,
    }


@router.get(
    "/lab-technician-test",
    summary="[TEST] Lab Technician and Admin endpoint",
    description="Accessible by 'admin' and 'lab_technician'. Receptionists will receive 403 Forbidden.",
)
def lab_technician_test(
    current_user: UserResponse = Depends(
        require_roles(UserRole.ADMIN, UserRole.LAB_TECHNICIAN)
    ),
):
    return {
        "status": "success",
        "message": "Access granted: Lab Technician/Admin authorized.",
        "authorizedRole": current_user.role,
        "userId": current_user.userId,
        "labId": current_user.labId,
    }


@router.get(
    "/lab-isolation-test",
    summary="[TEST] Laboratory tenant isolation verification",
    description="Verifies that the requested resource's labId matches the user's authoritative labId from JWT.",
)
def lab_isolation_test(
    resourceLabId: str = Query(
        ...,
        description="The labId of the resource being requested to verify tenant boundary",
    ),
    current_user: UserResponse = Depends(get_current_user),
    authenticated_lab_id: str = Depends(get_current_lab_id),
):
    # Verify tenant boundary
    ensure_lab_access(resourceLabId, current_user)

    return {
        "status": "success",
        "message": "Tenant boundary verified: Resource belongs to authenticated laboratory.",
        "userLabId": authenticated_lab_id,
        "resourceLabId": resourceLabId,
    }
