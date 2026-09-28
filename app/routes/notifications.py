from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field
from app.core.roles import UserRole
from app.dependencies.rbac import require_role
from app.schemas.auth import UserResponse

router = APIRouter(prefix="/notifications", tags=["Notifications"])


class SendNotificationRequest(BaseModel):
    recipientRole: str = Field(..., description="Target role: all, receptionist, lab_technician")
    message: str = Field(..., min_length=1, description="Message content")


@router.get(
    "",
    summary="List laboratory notifications (Admin Only)",
    description="Accessible ONLY by Admin. Receptionist and Lab Technician receive 403 Forbidden.",
)
def list_notifications(
    current_user: UserResponse = Depends(require_role(UserRole.ADMIN)),
):
    return {
        "status": "success",
        "module": "notifications",
        "labId": current_user.labId,
        "total": 0,
        "notifications": [],
    }


@router.post(
    "/broadcast",
    status_code=status.HTTP_201_CREATED,
    summary="Broadcast notification (Admin Only)",
    description="Accessible ONLY by Admin. Receptionist and Lab Technician receive 403 Forbidden.",
)
def broadcast_notification(
    data: SendNotificationRequest,
    current_user: UserResponse = Depends(require_role(UserRole.ADMIN)),
):
    return {
        "status": "success",
        "message": "Notification broadcast sent",
        "module": "notifications",
        "labId": current_user.labId,
        "recipientRole": data.recipientRole,
        "sender": current_user.userId,
    }
