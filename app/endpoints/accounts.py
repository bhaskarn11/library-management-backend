from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import users
from app import models
# from app.services.account import change_email
from app.utils.helper import create_token, hash_password
from app.utils.emailer import confirm_email
from app.services.auth import authenticate_user, request_otp, verify_otp, get_current_active_user


router = APIRouter(
    prefix="/accounts",
    tags=["Account API"]
)


@router.post("/reset-password/request")
def reset_password_request(payload: users.ResetPasswordRequest, db: Session = Depends(get_db)):
    success, res = request_otp(payload.email, db)
    if success and res:
        return {"success": True, "message": "Otp sent successfully"}
    else:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, {"success": False, "message": "Request Failed"})


@router.post("/reset-password")
def reset_password(payload: users.ResetPassword, db: Session = Depends(get_db)):
    verified = verify_otp(payload.email, payload.otp, db)
    if verified:
        db_user = db.query(users.User).filter_by(email=payload.email).first()
        db_user.hashed_password = hash_password(payload.new_password)
        db.commit()

        return {"success": True, "message": "Password reset successfully"}
    return HTTPException(status.HTTP_401_UNAUTHORIZED, {"success": False, "message": "Unauthorized"})
 

@router.post("/email-change")
def email_change_request(payload: users.EmailChangeRequest, 
                         task: BackgroundTasks,
                         user: models.User = Depends(get_current_active_user), db: Session = Depends(get_db)):

    if user:
        user.email = payload.new_email
        db.commit()
        _, otp = request_otp(payload.new_email, db)
        task.add_task(confirm_email, payload.new_email, otp)
        return {"success": True, "message": "Email Changed successfully"}
    raise HTTPException(status.HTTP_401_UNAUTHORIZED, 
                        detail={"success": False, "message": "Email Change failed"})


@router.post("/verify-email")
def verify_email(payload: users.VerifyEmail, db: Session = Depends(get_db)):
    user = db.query(models.User).filter_by(id=payload.user_id).first()
    if user:
        success = verify_otp(user.email, payload.otp, db)
        if success:
            user.email_verified = True
            db.commit()
        
            return {"success": True, "message": "Email verified successfully"}
    
    return HTTPException(status.HTTP_403_FORBIDDEN, 
                         detail={"success": False, "message": "Email verfication failed"})


# @router.post("/request-otp")
# def request_otp(payload: users.RequestOtp, task: BackgroundTasks, db: Session = Depends(get_db)):
#     _, otp = request_otp(payload.credential_value, db)
#     if payload.credential_type == users.CredentialType.EMAIL_VERIFY:
        
#         task.add_task(confirm_email, payload.credential_value, otp)
#     elif payload.credential_type == users.CredentialType.PHONE_VERIFY:
#         task.add_task(confirm_email, payload.credential_value, otp)
#     return {"success": True, "message": "Email Changed successfully"}
