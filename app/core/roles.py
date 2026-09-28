from enum import Enum
from typing import Set


class UserRole(str, Enum):
    """
    Standardized application user roles for Role-Based Access Control (RBAC).
    """
    ADMIN = "admin"
    RECEPTIONIST = "receptionist"
    LAB_TECHNICIAN = "lab_technician"


ALL_ROLES: Set[UserRole] = {
    UserRole.ADMIN,
    UserRole.RECEPTIONIST,
    UserRole.LAB_TECHNICIAN,
}
