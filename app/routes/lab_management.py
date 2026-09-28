from typing import List
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.core.roles import UserRole
from app.dependencies.rbac import require_role
from app.schemas.auth import UserResponse

router = APIRouter(prefix="/lab-management", tags=["Lab Management"])


class UpdateDepartmentsRequest(BaseModel):
    departments: List[str]


@router.get(
    "/departments",
    summary="Get laboratory departments and instruments (Admin Only)",
    description="Accessible ONLY by Admin. Receptionist and Lab Technician receive 403 Forbidden.",
)
def get_departments(
    current_user: UserResponse = Depends(require_role(UserRole.ADMIN)),
):
    return {
        "status": "success",
        "module": "lab-management",
        "labId": current_user.labId,
        "departments": [
            {"id": "DEP-01", "name": "Clinical Pathology"},
            {"id": "DEP-02", "name": "Biochemistry"},
            {"id": "DEP-03", "name": "Hematology"},
        ],
    }


@router.put(
    "/departments",
    summary="Update departments (Admin Only)",
    description="Accessible ONLY by Admin. Receptionist and Lab Technician receive 403 Forbidden.",
)
def update_departments(
    data: UpdateDepartmentsRequest,
    current_user: UserResponse = Depends(require_role(UserRole.ADMIN)),
):
    return {
        "status": "success",
        "message": "Departments updated successfully",
        "module": "lab-management",
        "labId": current_user.labId,
        "updatedBy": current_user.userId,
    }
