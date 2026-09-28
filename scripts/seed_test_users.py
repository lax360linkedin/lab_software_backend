import os
import sys
import uuid
from datetime import datetime, timezone

# Ensure backend package can be imported
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import get_database, init_db
from app.core.security import hash_password
from app.core.roles import UserRole


def seed_test_users():
    """
    Safely creates or updates test users for RBAC testing in development.
    Does NOT affect or weaken production signup security.
    """
    init_db()
    database = get_database()
    now_iso = datetime.now(timezone.utc).isoformat()

    # Find an existing laboratory or create a dedicated test laboratory
    lab = database.labs.find_one()
    if not lab:
        lab_id = "LAB-DEMO01"
        lab = {
            "labId": lab_id,
            "labName": "Apex Diagnostic Laboratories",
            "phone": "9876543210",
            "address": "100 Medical Center Parkway, Suite 500",
            "createdAt": now_iso,
        }
        database.labs.insert_one(lab)
        print(f"Created demo laboratory: {lab['labName']} ({lab['labId']})")
    else:
        print(f"Using existing laboratory: {lab['labName']} ({lab['labId']})")

    lab_id = lab["labId"]
    lab_name = lab["labName"]

    test_users = [
        {
            "name": "Dr. Alice Admin",
            "email": "admin@testlab.com",
            "password": "AdminPassword123!",
            "role": UserRole.ADMIN.value,
            "phone": "9876543210",
        },
        {
            "name": "Rachel Receptionist",
            "email": "receptionist@testlab.com",
            "password": "ReceptionistPass123!",
            "role": UserRole.RECEPTIONIST.value,
            "phone": "9876543211",
        },
        {
            "name": "Leo Lab Technician",
            "email": "technician@testlab.com",
            "password": "TechnicianPass123!",
            "role": UserRole.LAB_TECHNICIAN.value,
            "phone": "9876543212",
        },
    ]

    print("\n" + "=" * 60)
    print("SEEDING RBAC TEST USERS")
    print("=" * 60)

    for user_info in test_users:
        normalized_email = user_info["email"].strip().lower()
        existing = database.users.find_one({"email": normalized_email})

        user_id = existing["userId"] if existing else f"USR-{uuid.uuid4().hex[:8].upper()}"
        pwd_hash = hash_password(user_info["password"])

        doc = {
            "userId": user_id,
            "labId": lab_id,
            "labName": lab_name,
            "name": user_info["name"],
            "email": normalized_email,
            "phone": user_info["phone"],
            "passwordHash": pwd_hash,
            "role": user_info["role"],
            "isActive": True,
            "updatedAt": now_iso,
        }

        if not existing:
            doc["createdAt"] = now_iso
            database.users.insert_one(doc)
            print(f"[CREATED] Role: {user_info['role']:<15} | Email: {user_info['email']:<25} | Password: {user_info['password']}")
        else:
            database.users.update_one({"email": normalized_email}, {"$set": doc})
            print(f"[UPDATED] Role: {user_info['role']:<15} | Email: {user_info['email']:<25} | Password: {user_info['password']}")

    print("=" * 60)
    print("Seed complete! All 3 roles are ready for Postman testing.\n")


if __name__ == "__main__":
    seed_test_users()
