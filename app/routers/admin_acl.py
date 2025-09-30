from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..deps import get_db, get_current_user
from .. import crud
from ..schemas import RoleCreate, RoleOut, ResourceCreate, PermissionCreate, RolePermissionCreate, UserRoleAssign
from ..models import User

router = APIRouter(prefix="/admin", tags=["admin"])


def ensure_admin(user: User = Depends(get_current_user)):
    if not user.is_staff:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required.")
    return user


@router.post("/roles", response_model=RoleOut)
def create_role(payload: RoleCreate, db: Session = Depends(get_db), _: User = Depends(ensure_admin)):
    r = crud.create_role(db, name=payload.name, description=payload.description)
    return RoleOut(id=r.id, name=r.name, description=r.description)


@router.post("/resources")
def create_resource(payload: ResourceCreate, db: Session = Depends(get_db), _: User = Depends(ensure_admin)):
    res = crud.create_resource(db, name=payload.name, description=payload.description)
    return {"id": res.id, "name": res.name}


@router.post("/permissions")
def create_permission(payload: PermissionCreate, db: Session = Depends(get_db), _: User = Depends(ensure_admin)):
    p = crud.create_permission(db, action=payload.action, description=payload.description)
    return {"id": p.id, "action": p.action}


@router.post("/role-permissions")
def create_role_permission(payload: RolePermissionCreate, db: Session = Depends(get_db),
                           _: User = Depends(ensure_admin)):
    rp = crud.create_role_permission(db, role_id=payload.role_id, resource_id=payload.resource_id,
                                     permission_id=payload.permission_id)
    return {"id": rp.id}


@router.post("/assign-role")
def assign_role(payload: UserRoleAssign, db: Session = Depends(get_db), _: User = Depends(ensure_admin)):
    ur = crud.assign_role_to_user(db, user_id=payload.user_id, role_id=payload.role_id)
    return {"id": ur.id}
