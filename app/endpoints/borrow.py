from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session

from app import models
from app.database import get_db
from app.schemas.borrows import BorrowCreate, Borrow, BorrowReturn
from app.services.borrow import create_borrow, return_borrow
from app.utils.emailer import borrow_notification, borrow_due_reminder

router = APIRouter(
    prefix="/borrow",
    # dependencies=[Depends(get_current_active_user)]
)


@router.post("/issue", response_model=Borrow, tags=["Borrow Endpoint"])
def create_borrow_order(borrow: BorrowCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    if len(borrow.items) > 5:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="More than 5 item not allowed")
    item_ids = [item.item_id for item in borrow.items[:5]]  # only five items are allowed
    items = db.query(models.Item).filter(models.Item.id.in_(item_ids),
                                         models.Item.available == True).limit(5).all()
    if not items:
        return HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Items not found")

    try:
        db_b = create_borrow(borrow, items, db)

        background_tasks.add_task(borrow_notification, db_b, 'ISSUE')
        return db_b

    except Exception as e:
        # print(e)
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Problem creating borrow request")


@router.post("/return", response_model=Borrow, tags=["Borrow Endpoint"])
def return_borrow_order(borrow: BorrowReturn, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    try:
        db_b = return_borrow(borrow.borrow_id, db)
        background_tasks.add_task(borrow_notification, db_b, 'RETURN')
        return db_b
    except Exception as e:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Problem returning borrow request")


@router.post("/renew", tags=["Borrow Endpoint"])
def renew_borrow_order(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    pass
