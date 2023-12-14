from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from pydantic import EmailStr

from app.database import get_db
from app.schemas import users, token
from app.services.auth import authenticate_user, get_current_active_user, get_current_user, request_otp, verify_otp
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
    return current_user


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


@router.post("/reset-password/request")
def reset_password_request(payload: users.ResetPasswordRequest, db: Session = Depends(get_db)):
    res = request_otp(payload.email, db)
    if res:
        return {"success": True, "message": "Otp sent successfully"}
    else:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, {"success": False, "message": "Request Failed"})


@router.post("/rest-password")
def reset_password(payload: users.ResetPassword, db: Session = Depends(get_db)):
    verified = verify_otp(payload.email, payload.otp, db)
    if verified:
        db_user = db.query(users.User).filter_by(email=payload.email).first()
        db_user.hashed_password = hash_password(payload.new_password)
        db.commit()

        return {"success": True, "message": "Password reset successfully"}
    return HTTPException(status.HTTP_401_UNAUTHORIZED, {"success": False, "message": "Unauthorized"})
    
