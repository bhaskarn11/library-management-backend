from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import users
from app.services.user import create_user, get_user_by_id, update_user, remove_user_by_id
from app.utils.emailer import confirm_email
from app.services.auth import request_otp

router = APIRouter(
    prefix="/users"
)


@router.get("/{id}", response_model=users.User, tags=["Users"])
def get_user(id: int, db: Session = Depends(get_db)):

    user = get_user_by_id(db, id)
    if user:
        return user
    raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User Not Found")


@router.post("/", tags=["Users"])
def post_user(user: users.UserCreate, task: BackgroundTasks, db: Session = Depends(get_db)):
    user = create_user(db, user)
    if user:
        sent, otp = request_otp(user.email, db)
        if sent: task.add_task(confirm_email, user.email, otp)
        return user
    
    return HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail={"success": False, "message": "Could not create user"})


@router.patch("/{id}", tags=["Users"])
def patch_user(id: int, user: users.UserUpdate, db: Session = Depends(get_db)):
    return update_user(db, user, id)


@router.delete("/{user_id}", tags=["Users"])
def delete_user(user_id: int, db: Session = Depends(get_db)):
    success = remove_user_by_id(db, user_id)
    if success:
        return {"status": success, "detail": "User deleted"}
    else:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


