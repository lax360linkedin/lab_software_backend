from typing import TypedDict, Optional


class LabDocument(TypedDict):
    labId: str
    labName: str
    phone: str
    address: str
    createdAt: str


class UserDocument(TypedDict):
    userId: str
    labId: str
    labName: str
    name: str
    email: str
    phone: str
    passwordHash: str
    role: str
    isActive: bool
    createdAt: str
    updatedAt: str
