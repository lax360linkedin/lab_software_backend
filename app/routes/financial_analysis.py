from fastapi import APIRouter, Depends
from app.core.roles import UserRole
from app.dependencies.rbac import require_role
from app.schemas.auth import UserResponse

router = APIRouter(prefix="/financial-analysis", tags=["Financial Analysis"])


@router.get(
    "/revenue",
    summary="Get revenue analytics (Admin Only)",
    description="Accessible ONLY by Admin. Receptionist and Lab Technician receive 403 Forbidden.",
)
def get_revenue_analytics(
    current_user: UserResponse = Depends(require_role(UserRole.ADMIN)),
):
    return {
        "status": "success",
        "module": "financial-analysis",
        "labId": current_user.labId,
        "financials": {
            "totalRevenue": 0.0,
            "monthlyRevenue": 0.0,
            "pendingReceivables": 0.0,
        },
    }


@router.get(
    "/collection-summary",
    summary="Get collections summary (Admin Only)",
    description="Accessible ONLY by Admin. Receptionist and Lab Technician receive 403 Forbidden.",
)
def get_collection_summary(
    current_user: UserResponse = Depends(require_role(UserRole.ADMIN)),
):
    return {
        "status": "success",
        "module": "financial-analysis",
        "labId": current_user.labId,
        "collections": {
            "today": 0.0,
            "thisWeek": 0.0,
            "thisMonth": 0.0,
        },
    }
