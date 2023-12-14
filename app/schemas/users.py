from pydantic import BaseModel, EmailStr
from typing import Union, List, Literal, Any, Dict
from datetime import date
from enum import Enum
from app.schemas.borrows import Borrow


class UserBase(BaseModel):
    name: str
    email: EmailStr
    type: str


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    name: Union[str, None]
    email: Union[EmailStr, None]
    type: Union[str, None]


class User(UserBase):
    id: int
    join_date: date
    disabled: bool
    type: Enum
    borrows: List[Borrow] = []

    class Config:
        orm_mode = True


class ResetPasswordRequest(BaseModel):
    email: EmailStr


class ResetPassword(BaseModel):
    email: EmailStr
    otp: str
    new_password: str
