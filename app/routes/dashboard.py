from fastapi import APIRouter, Depends
from app.core.roles import UserRole
from app.dependencies.rbac import require_roles
from app.schemas.auth import UserResponse

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get(
    "/summary",
    summary="Get laboratory dashboard summary",
    description="Accessible by Admin, Receptionist, and Lab Technician. Returns metrics scoped to the user's laboratory.",
)
def get_dashboard_summary(
    current_user: UserResponse = Depends(
        require_roles(UserRole.ADMIN, UserRole.RECEPTIONIST, UserRole.LAB_TECHNICIAN)
    ),
):
    return {
        "status": "success",
        "module": "dashboard",
        "labId": current_user.labId,
        "role": current_user.role,
        "data": {
            "pendingTests": 0,
            "todayPatients": 0,
            "todaySamples": 0,
            "completedReports": 0,
        },
    }


@router.get(
    "/activity",
    summary="Get recent dashboard activity",
    description="Accessible by Admin, Receptionist, and Lab Technician.",
)
def get_dashboard_activity(
    current_user: UserResponse = Depends(
        require_roles(UserRole.ADMIN, UserRole.RECEPTIONIST, UserRole.LAB_TECHNICIAN)
    ),
):
    return {
        "status": "success",
        "module": "dashboard",
        "labId": current_user.labId,
        "activities": [],
    }
