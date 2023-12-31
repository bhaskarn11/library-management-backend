from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.dialects.postgresql import insert
from fastapi import HTTPException, Depends, status
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta

from app.services.user import get_user_by_username
from app import models
from app.schemas import users
from app.database import get_db
from app.config import settings
from app.utils.helper import verify_password_hash, generate_otp

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login", scopes=settings.AUTH_SCOPES)


def authenticate_user(db: Session, username: str, password: str):
    user = get_user_by_username(db, username)
    if not user:
        return False
    if not verify_password_hash(password, user.hashed_password):
        return False
    return user



def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        # print(payload)
        username: str = payload.get("sub")
        if username is None:
            return credentials_exception
        # token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = db.query(models.User).filter_by(email=username).first()
    if user is None:
        raise credentials_exception
    return user
    
    
def get_current_active_user(current_user: users.User = Depends(get_current_user)):
    if not current_user.disabled:
        return current_user


def request_otp(email: str, db: Session):

    otp = generate_otp()
    db_user = db.query(models.User).filter_by(email=email).first()
    if db_user:
        data = {
            "user_id": db_user.id,
            "code": otp,
            "expire_timestamp": datetime.now(timezone.utc) + timedelta(minutes=10)
        }

        stmt = insert(models.Otp).values(data)
        upsert_stmt = stmt.on_conflict_do_update(
            index_elements=["user_id", "code"],
            set_= data
        )

        db.execute(upsert_stmt)
        db.commit()
        return (True, otp)
    return (False, None)


def verify_otp(email: str, otp: str, db:Session):
    time = datetime.now()
    user = db.query(models.User).filter_by(email=email).first()
    if user:
        match = db.query(models.Otp).filter_by(user_id=user.id, code=otp).first()

        if match and match.expire_timestamp.timestamp() < time.timestamp():
            db.delete(match)
            db.commit()
            return True
        return False
    return False
