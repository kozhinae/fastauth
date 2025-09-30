from sqlalchemy.orm import Session
from sqlalchemy import select, and_
from . import models
from datetime import datetime, timedelta
import secrets
from .config import settings

TOKEN_LIFETIME = timedelta(minutes=settings.TOKEN_LIFETIME_MINUTES)


def get_user_by_email(db: Session, email: str):
    return db.execute(select(models.User).where(models.User.email == email)).scalars().first()


def create_user(db: Session, email: str, password: str, first_name=None, last_name=None, middle_name=None):
    u = models.User(email=email, first_name=first_name, last_name=last_name, middle_name=middle_name)
    u.set_password(password)
    db.add(u)
    db.commit()
    db.refresh(u)
    return u


def get_user(db: Session, user_id: str):
    return db.get(models.User, user_id)


def create_token_for_user(db: Session, user: models.User):
    token = secrets.token_urlsafe(32)
    now = datetime.utcnow()
    at = models.AuthToken(user_id=user.id, token=token, created_at=now, expires_at=now + TOKEN_LIFETIME)
    db.add(at)
    db.commit()
    db.refresh(at)
    return at


def get_token(db: Session, token_str: str):
    return db.execute(select(models.AuthToken).where(models.AuthToken.token == token_str,
                                                     models.AuthToken.is_active == True)).scalars().first()


def revoke_token(db: Session, token_obj: models.AuthToken):
    token_obj.revoke()
    db.add(token_obj)
    db.commit()


def revoke_all_tokens_for_user(db: Session, user: models.User):
    db.execute(
        models.AuthToken.__table__.update().where(models.AuthToken.user_id == user.id).values(is_active=False)
    )
    db.commit()


def create_role(db: Session, name: str, description: str = None):
    r = models.Role(name=name, description=description)
    db.add(r)
    db.commit()
    db.refresh(r)
    return r


def create_resource(db: Session, name: str, description: str = None):
    res = models.Resource(name=name, description=description)
    db.add(res)
    db.commit()
    db.refresh(res)
    return res


def create_permission(db: Session, action: str, description: str = None):
    p = models.Permission(action=action, description=description)
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


def create_role_permission(db: Session, role_id: int, resource_id: int, permission_id: int):
    rp = models.RolePermission(role_id=role_id, resource_id=resource_id, permission_id=permission_id)
    db.add(rp)
    db.commit()
    db.refresh(rp)
    return rp


def assign_role_to_user(db: Session, user_id: str, role_id: int):
    ur = models.UserRole(user_id=user_id, role_id=role_id)
    db.add(ur)
    db.commit()
    db.refresh(ur)
    return ur


def get_user_role_ids(db: Session, user_id: str):
    rows = db.execute(select(models.UserRole.role_id).where(models.UserRole.user_id == user_id)).scalars().all()
    return rows


def check_role_permission(db: Session, role_ids: list[int], resource_name: str, action: str) -> bool:
    res = db.execute(select(models.Resource).where(models.Resource.name == resource_name)).scalars().first()
    perm = db.execute(select(models.Permission).where(models.Permission.action == action)).scalars().first()
    if not res or not perm:
        return False
    rows = db.execute(
        select(models.RolePermission).where(
            models.RolePermission.role_id.in_(role_ids),
            models.RolePermission.resource_id == res.id,
            models.RolePermission.permission_id == perm.id
        )
    ).scalars().first()
    return rows is not None
