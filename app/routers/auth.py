from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from .. import schemas, crud
from ..deps import get_db, get_current_user
from ..schemas import RegisterIn, LoginIn, TokenOut
from ..models import User
from ..utils import iso

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", status_code=201)
def register(payload: RegisterIn, db: Session = Depends(get_db)):
    if payload.password != payload.password2:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Passwords do not match.")
    if crud.get_user_by_email(db, payload.email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered.")
    user = crud.create_user(db, email=payload.email, password=payload.password,
                            first_name=payload.first_name, last_name=payload.last_name, middle_name=payload.middle_name)
    return {"id": user.id, "email": user.email}


@router.post("/login", response_model=TokenOut)
def login(payload: LoginIn, db: Session = Depends(get_db)):
    u = crud.get_user_by_email(db, payload.email)
    if not u or not u.check_password(payload.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials.")
    if not u.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Account inactive.")
    token_obj = crud.create_token_for_user(db, u)
    return TokenOut(token=token_obj.token, expires_at=token_obj.expires_at)


@router.post("/logout")
def logout(request: Request, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    auth = request.headers.get("Authorization")
    token_str = auth[len("Token "):].strip() if auth and auth.startswith("Token ") else None
    if not token_str:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token required.")
    token_obj = crud.get_token(db, token_str)
    if not token_obj:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token.")
    crud.revoke_token(db, token_obj)
    return {"detail": "logged out"}
