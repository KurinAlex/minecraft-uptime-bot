from sqlalchemy import Boolean, Integer, String
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(AsyncAttrs, DeclarativeBase):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)


class User(Base):
    __tablename__ = "user"

    chat_id: Mapped[int] = mapped_column(Integer, unique=True)
    is_subscribed: Mapped[bool] = mapped_column(Boolean, default=False)


class ServerData(Base):
    __tablename__ = "server_data"

    key: Mapped[str] = mapped_column(String, unique=True)
    value: Mapped[str] = mapped_column(String)
