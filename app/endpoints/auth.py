from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from pydantic import EmailStr

from app.database import get_db
from app.schemas import users, token
from app.services.auth import authenticate_user, get_current_active_user, get_current_user
from app.utils.helper import create_token, hash_password

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post("/login", response_model=token.Token)
def login_for_access_token(response: Response, form_data: OAuth2PasswordRequestForm = Depends(),
                           db: Session = Depends(get_db)):

    user = authenticate_user(db, form_data.username, form_data.password)
    if user:
        token = create_token({"sub": form_data.username})
        refresh_token = create_token({"sub": user.username}, timedelta(days=1))
        response.set_cookie(
            "refreshToken", refresh_token, secure=True,
            httponly=True, samesite="none", max_age=7*24*60*1000)

        return {"access_token": token, "token_type": "bearer"}
    return HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Unauthorized Access or User not found")


@router.get("/verify", response_model=users.User)
def read_users_me(current_user: users.User = Depends(get_current_active_user)):
    if current_user:
        return current_user
    
    raise HTTPException(status_code=400, detail="Inactive user")


@router.post("/refresh", response_model=token.Token)
def refresh_access_token(req: Request, res: Response, db: Session = Depends(get_db)):
    cookies = req.cookies
    if not cookies.get("refreshToken"):
        return HTTPException(status.HTTP_401_UNAUTHORIZED, detail={"message": "Unauthorized Access"})
    refresh_token = cookies.get("refreshToken")
    try:
        user = get_current_user(refresh_token, db)

        access_token = create_token({"sub": user.username})
        return {"access_token": access_token, "token_type": "bearer"}
    except HTTPException as e:
        raise e


