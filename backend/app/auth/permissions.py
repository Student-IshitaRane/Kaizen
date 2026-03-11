from fastapi import HTTPException, status
from app.database.models import UserRole

def require_role(allowed_roles: list[UserRole]):
    def decorator(user_role: UserRole):
        if user_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return True
    return decorator

def is_auditor(user_role: UserRole) -> bool:
    return user_role == UserRole.AUDITOR or user_role == UserRole.ADMIN

def is_finance(user_role: UserRole) -> bool:
    return user_role == UserRole.FINANCE or user_role == UserRole.ADMIN

def is_admin(user_role: UserRole) -> bool:
    return user_role == UserRole.ADMIN
