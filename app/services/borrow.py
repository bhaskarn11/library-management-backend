from sqlalchemy.orm import Session
from app import models
from app.schemas import borrows
from datetime import datetime, timedelta
from typing import List, Type
from fastapi import HTTPException


def create_borrow(borrow: borrows.BorrowCreate, items: List[Type[models.Item]], db: Session):
    t = datetime.utcnow()
    
    for item in items:
            item.available = False

    db_borrow = models.Borrow(borrower_id=borrow.borrower_id, items=items)
    db_borrow.issue_date = t
    db_borrow.due_date = t + timedelta(days=15)
    db.add(db_borrow)
    db.commit()
    db.refresh(db_borrow)
    return db_borrow


def return_borrow(borrow_id: int, db: Session):
    db_borrow = db.query(models.Borrow).filter_by(id=borrow_id).first()
    if db_borrow:
        db_borrow.status = models.BorrowStatus.RETURNED
        for item in db_borrow.items:
            item.available = False

        db.commit()
        db.refresh(db_borrow)

        return db_borrow
    else:
        raise Exception("Error")


def renew_borrow(borrow_id: int, db: Session):
    db_borrow = db.query(models.Borrow).filter_by(id=borrow_id).first()

    if db_borrow:
        db_borrow.status = models.BorrowStatus.RENEWED
        db_borrow.due_date = db_borrow.due_date + timedelta(days=7)
        for item in db_borrow.items:
            item.available = False

        db.commit()
        db.refresh(db_borrow)

        return db_borrow
    else:
        raise Exception("Error")
