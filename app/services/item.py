from sqlalchemy.orm import Session
from app import models
from app.schemas import items


def get_item_by_id(id: int, db: Session):
    db_item = db.query(models.Item).filter_by(id=id).first()
    return db_item


def create_item(item: items.ItemCreate, db: Session):
    tags = db.query(models.ItemTags).filter(models.ItemTags.tag.in_(item.tags[0:5])).all()
    # print(tags)
    db_item = models.Item(title=item.title, description=item.description,
                           author=item.author, publisher=item.publisher, 
                           publish_date=item.publish_date, isbn=item.isbn, available=item.available,
                            type=item.type, tags=tags)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    print(db_item)
    return db_item


def update_item(item: items.ItemUpdate, id: int, db: Session):
    # print(item)
    db_item = db.query(models.Item).filter_by(id=id).first()
    db_item.title = item.title if item.title else db_item.title
    db_item.description = item.description if item.description else db_item.description
    db_item.isbn = item.isbn if item.isbn else db_item.isbn
    db_item.type = item.type if item.type else db_item.type
    db_item.publisher = item.publisher if item.publisher else db_item.publisher

    db.commit()
    db.refresh(db_item)
    return db_item


def remove_item(id: int, db: Session):
    i = db.query(models.Item).filter_by(id=id)
    i.delete()
    db.commit()
    # db.refresh()
    return i


def get_tags_list(q: str, db: Session, skip: int, limit: int):
    tags = db.query(models.ItemTags).filter(models.ItemTags.tag.ilike(f"%{q}%")).offset(skip).limit(limit).all()
    return tags


def add_tag(db: Session, tags: list[str]):
    try:
        db_tags = []
        for tag in tags:
            db_tag = models.ItemTags(tag=tag)
            db_tags.append(db_tag)

        db.add_all(db_tags)
        db.commit()
        # db.refresh(db_tags)
        return True
    except Exception as e:
        return False
