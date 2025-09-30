from fastapi import HTTPException, status, Depends
from . import crud
from sqlalchemy.orm import Session
from .deps import get_db, get_current_user


def require_permission(resource_name: str, action: str):
    def dependency(user=Depends(get_current_user), db: Session = Depends(get_db)):
        if getattr(user, "is_staff", False):
            return True
        role_ids = crud.get_user_role_ids(db, user.id)
        if not role_ids:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden.")
        allowed = crud.check_role_permission(db, role_ids, resource_name, action)
        if not allowed:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden.")
        return True

    return dependency
