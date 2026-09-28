from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field
from app.core.roles import UserRole
from app.dependencies.rbac import require_role
from app.schemas.auth import UserResponse

router = APIRouter(prefix="/expenses", tags=["Expenses"])


class RecordExpenseRequest(BaseModel):
    category: str = Field(..., description="Expense category e.g., Reagents, Utilities, Maintenance")
    amount: float = Field(..., gt=0, description="Expense amount")
    description: str = Field(..., description="Expense notes/description")


@router.get(
    "",
    summary="List laboratory expenses (Admin Only)",
    description="Accessible ONLY by Admin. Receptionist and Lab Technician receive 403 Forbidden.",
)
def list_expenses(
    current_user: UserResponse = Depends(require_role(UserRole.ADMIN)),
):
    return {
        "status": "success",
        "module": "expenses",
        "labId": current_user.labId,
        "total": 0,
        "expenses": [],
    }


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Record laboratory expense (Admin Only)",
    description="Accessible ONLY by Admin. Receptionist and Lab Technician receive 403 Forbidden.",
)
def record_expense(
    data: RecordExpenseRequest,
    current_user: UserResponse = Depends(require_role(UserRole.ADMIN)),
):
    return {
        "status": "success",
        "message": "Expense recorded successfully",
        "module": "expenses",
        "labId": current_user.labId,
        "expense": {
            "category": data.category,
            "amount": data.amount,
            "description": data.description,
            "recordedBy": current_user.userId,
        },
    }
