from pydantic import BaseModel
from typing import Union, List, Literal, Any, Dict
from datetime import date
from app.schemas.items import Item


class BorrowItem(BaseModel):
    item_id: int


class BorrowCreate(BaseModel):
    borrower_id: int
    action_type: Literal["ISSUE", "RETURN"]
    items: List[BorrowItem]


class BorrowReturn(BaseModel):
    borrower_id: int
    action_type: Literal["ISSUE", "RETURN"]
    borrow_id: int


class Borrow(BaseModel):
    id: int
    issue_date: date
    due_date: date
    items: List[Item]

    class Config:
        orm_mode = True
