# app/auth/dependencies.py
from fastapi import Depends, HTTPException, status, Request
from app.auth.engine import ABACEngine
from types import SimpleNamespace
from fastapi import Depends
from fastapi import Path
# موتور ABAC رو global نگه می‌داریم

engine = ABACEngine()

def get_current_user2():
    # کاربر فرضی برای تست
    return {
        "id": 20,
        "username": "seller_user",
        "roles": ["seller"],
        "attributes": {
            "is_active": True,
            "department": "management"
        }
    }


def authorize(action: str, resource_type: str):
    """
    Dependency برای بررسی دسترسی ABAC.
    """
    def dependency(
        product_id: int = Path(...),
        current_user: dict = Depends(get_current_user2)):
        
        context = { 
            "user": current_user,
            "resource": {"type": resource_type, "id": product_id },
            "action": action,
            "env": {"hour": 10},  # فرضی برای تست
        }
        allowed = engine.check_access(context)
        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User '{current_user['username']}' is not authorized for '{action}' on '{resource_type}'",
            )
        return True

    return dependency



