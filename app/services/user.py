from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Type
from fastapi import HTTPException, status

from app import models
from app.schemas import users
from app.utils.helper import hash_password


def get_user_by_username(db: Session, username: str):
    user = db.query(models.User).filter_by(email=username).first()
    return user


def get_user_by_id(db: Session, id: int):
    user = db.query(models.User).filter_by(id=id).first()
    return user


def create_user(db: Session, user: users.UserCreate):
    db_user = models.User(name=user.name, email=user.email, type=user.type)
    db_user.hashed_password = hash_password(user.password)
    db_user.join_date = datetime.utcnow()
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, user: users.UserUpdate, id: int):
    db_user = db.query(models.User).filter_by(id=id).first()
    db_user.username = user.email if user.email else db_user.email
    db_user.name = user.name if user.name else db_user.name
    db_user.type = user.type if user.type else db_user.type
    db.commit()
    db.refresh(db_user)
    return db_user


def remove_user_by_id(db: Session, id: int):

    db_user = db.query(models.User).filter_by(id=id)
    if db_user:
        db_user.delete()
        db.commit()
        return True
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
