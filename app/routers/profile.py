from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..deps import get_db, get_current_user
from ..schemas import ProfileOut
from ..models import User
from .. import crud

router = APIRouter(prefix="/auth", tags=["profile"])


@router.get("/profile", response_model=ProfileOut)
def get_profile(user: User = Depends(get_current_user)):
    return ProfileOut(
        id=user.id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        middle_name=user.middle_name,
        is_active=user.is_active,
    )


@router.patch("/profile", response_model=ProfileOut)
def update_profile(payload: dict, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    allowed = {"first_name", "last_name", "middle_name"}
    changed = False
    for k, v in payload.items():
        if k in allowed:
            setattr(user, k, v)
            changed = True
    if changed:
        db.add(user)
        db.commit()
        db.refresh(user)
    return ProfileOut(
        id=user.id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        middle_name=user.middle_name,
        is_active=user.is_active,
    )


@router.delete("/profile")
def delete_profile(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    user.soft_delete()
    db.add(user)
    db.commit()
    crud.revoke_all_tokens_for_user(db, user)
    return {"detail": "account soft-deleted"}
