from sqlalchemy import Boolean, Column, Integer
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase


class Base(AsyncAttrs, DeclarativeBase):
    id = Column(Integer, primary_key=True)


class User(Base):
    __tablename__ = "user"

    chat_id = Column(Integer, unique=True)
    is_subscribed = Column(Boolean, default=False)
