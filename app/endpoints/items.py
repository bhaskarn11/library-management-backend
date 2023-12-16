from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Any
from app.database import get_db
from app import models
from app.schemas.items import ItemCreate, ItemUpdate, Item, SearchQuery, SearchResult, SearchFilters

from app.services.item import get_item_by_id, create_item, remove_item, update_item, get_tags_list, add_tag
router = APIRouter(
    prefix="/items",
    # dependencies=[Depends(get_current_active_user)]
)


@router.get("/{id}", response_model=Item | None, tags=["Items"])
def get_items(id: int, db: Session = Depends(get_db)):

    item = get_item_by_id(id, db)
    if item:
        return item
    else:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Item bot found with this id")


@router.delete("/{id}", tags=["Items"])
def delete_items(id: int, db: Session = Depends(get_db)):
    try:
        return remove_item(id, db)
    except Exception as e:
        return HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.patch("/{id}", response_model=Item, tags=["Items"])
def patch_items(id: int, item: ItemUpdate, db: Session = Depends(get_db)):
    try:
        return update_item(item, id, db)
    except Exception as e:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error while processing")


@router.post("/", response_model=Item,tags=["Items"])
def post_items(item: ItemCreate, db: Session = Depends(get_db)):
    try:
        # print(item)
        return create_item(item, db)
    except Exception as e:
        print(e)
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Couldn't create item")


@router.post("/search", tags=["Items search endpoint"], response_model=SearchResult)
def search_items(search_query: SearchQuery, db: Session = Depends(get_db)):
    filters = search_query.filters
    res = db.query(models.Item).where(
        # publish_date=filters.publish_date,
        models.Item.title.ilike("%" + search_query.query + "%"),
        models.Item.available==filters.available,
        models.Item.type==filters.type,
        # models.Item.author.ilike(filters.author)
    ).offset(search_query.skip).limit(search_query.limit).all()

    fo: dict[str, set[Any]] = {}

    for item in res:
        d = item.__dict__
        d.pop("_sa_instance_state")
        f = SearchFilters.__fields__.keys()
        # print(filter)
        for key, val in d.items():
            if key in f:
                if fo.get(key):
                    fo.get(key).add(val)
                else:
                    fo.update({key: {val}})

    sr = SearchResult(results=res, filter_options=fo)

    return sr


@router.get("/tags/search", tags=["Item tag endpoint"])
def search_tags(q: str, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):

    tags = get_tags_list(q, db, skip, limit)

    return tags


@router.post("/tags", tags=["Item tag endpoint"])
def add_tags(tags: list[str], db: Session = Depends(get_db)):
    success = add_tag(db, tags)
    if success:
        return {"success": success, "message": "Tags added"}
    raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail={"success": success, "message": "Tags add failed"})
