from fastapi import Depends, HTTPException, status, Request
from .database import SessionLocal
from sqlalchemy.orm import Session
from . import crud, models
from datetime import datetime
from typing import Any


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(request: Request, db: Session = Depends(get_db)) -> Any:
    auth = request.headers.get("Authorization")
    if not auth or not auth.startswith("Token "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Authentication credentials were not provided.")
    token_str = auth[len("Token "):].strip()
    token_obj = crud.get_token(db, token_str)
    if not token_obj:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token.")
    if token_obj.expires_at < datetime.utcnow():
        token_obj.is_active = False
        db.add(token_obj)
        db.commit()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired.")
    user = token_obj.user
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User inactive.")
    return user
