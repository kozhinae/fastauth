from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class RegisterIn(BaseModel):
    email: EmailStr
    password: str
    password2: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    middle_name: Optional[str] = None


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class TokenOut(BaseModel):
    token: str
    expires_at: datetime


class ProfileOut(BaseModel):
    id: str
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    middle_name: Optional[str] = None
    is_active: bool



class RoleCreate(BaseModel):
    name: str
    description: Optional[str] = None


class RoleOut(RoleCreate):
    id: int


class ResourceCreate(BaseModel):
    name: str
    description: Optional[str] = None


class PermissionCreate(BaseModel):
    action: str
    description: Optional[str] = None


class RolePermissionCreate(BaseModel):
    role_id: int
    resource_id: int
    permission_id: int


class UserRoleAssign(BaseModel):
    user_id: str
    role_id: int
