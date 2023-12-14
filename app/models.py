from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Enum, Table
from sqlalchemy.orm import relationship, mapped_column, Mapped
from app.database import Base

from typing import List
import enum


class UserTypes(enum.Enum):
    BORROWER = "BORROWER"
    STAFF = "STAFF"
    ADMIN = "ADMIN"


class ItemTypes(enum.Enum):
    BOOK = "BOOK"
    JOURNAL = "JOURNAL"
    MAGAZINE = "MAGAZINE"
    NEWSPAPER = "NEWSPAPER"


class BorrowStatus(enum.Enum):
    RETURNED = "RETURNED"
    ISSUED = "ISSUED"
    RENEWED = "RENEWED"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    email_verified = Column(Boolean, default=False)
    hashed_password = Column(String)
    join_date = Column(DateTime)
    type = Column(Enum(UserTypes, name="UserTypes", create_constraint=True))
    disabled = Column(Boolean, default=False)
    
    borrows = relationship("Borrow", back_populates="borrower")


class Otp(Base):
    __tablename__ = "passcodes"

    expire_timestamp = Column(DateTime)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, primary_key=True)
    code = Column(String, primary_key=True)


# authors_items = Table(
#     "authors_items",
#     Base.metadata,
#     Column("author_id", ForeignKey("authors.id")),
#     Column("item_id", ForeignKey("items.id"))
# )


# class Author(Base):
#     __tablename__ = "authors"

#     id = Column(Integer, primary_key=True, index=True)
#     name = Column(String, unique=True)


class ItemTags(Base):
    __tablename__ = "item_tags"
    id = Column(Integer, primary_key=True, index=True)
    tag = Column(String)
    

items_tags = Table(
    "itmes_tags_association",
    Base.metadata,
    Column("tag_id", ForeignKey("item_tags.id")),
    Column("item_id", ForeignKey("items.id"))
)


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String, nullable=True)
    image_link = Column(String, nullable=True)
    isbn = Column(String, nullable=True, index=True)
    publish_date = Column(DateTime)
    publisher = Column(String)
    available = Column(Boolean, default=True)
    type = Column(Enum(ItemTypes, name="ItemTypes", create_constraint=True))

    # authors: Mapped[List[Author]] = relationship(secondary=authors_items)
    author = Column(String, nullable=True, index=True)
    tags: Mapped[List[ItemTags]] = relationship(secondary=items_tags)


borrows_items_association = Table(
    "borrows_items",
    Base.metadata,
    Column("borrow_id", ForeignKey("borrows.id")),
    Column("item_id", ForeignKey("items.id"))
)


class Borrow(Base):
    __tablename__ = "borrows"

    id = Column(Integer, primary_key=True, index=True)
    issue_date = Column(DateTime)
    due_date = Column(DateTime)
    items: Mapped[List[Item]] = relationship(secondary=borrows_items_association)
    # issuer_id = Column(Integer, ForeignKey("users.id"))
    status = Column(Enum(BorrowStatus, name="status", create_constraint=True))
    borrower_id = Column(Integer, ForeignKey("users.id"))

    borrower = relationship("User", back_populates="borrows")


# class AvailableItem(Base):
#     __tablename__ = "available_items"

#     item_id = mapped_column(ForeignKey("items.id"), primary_key=True)
