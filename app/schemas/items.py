from pydantic import BaseModel
from typing import Union, List, Literal, Any, Dict
from datetime import date

from app.models import ItemTypes


class ItemBase(BaseModel):
    title: str
    description: Union[str, None]
    isbn: str
    publisher: str
    type: ItemTypes


class ItemCreate(ItemBase):
    available: bool = True
    publish_date: date = '2022-02-01'
    author: str
    tags: list[str] = []


class ItemUpdate(ItemBase):
    title: Union[str, None]
    isbn: Union[str, None]
    publisher: Union[str, None]
    type: Union[ItemTypes, None]


class Item(ItemBase):
    id: int
    publish_date: date
    available: bool = True
    author: Union[str, None]

    class Config:
        orm_mode = True


class SearchFilters(BaseModel):
    publish_date: date | None
    available: bool | None
    type: ItemTypes | None
    author: str | None


class SearchResult(BaseModel):
    results: List[Item]
    filter_options: Dict[str, Any]


class SearchQuery(BaseModel):
    query: str
    filters: SearchFilters
    skip: int = 0
    limit: int = 10
