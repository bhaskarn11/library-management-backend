from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Type
from fastapi import HTTPException, status

from app import models
from app.schemas import users
from app.services.auth import authenticate_user


# def change_email(db: Session, user_id: int, new_email: str, password: str):
#     user = db.query(models.User).filter_by(id=user_id).first()
#     user.email = new_email
    
   
