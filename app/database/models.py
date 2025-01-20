from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy import BigInteger, String, ForeignKey

import os
from dotenv import load_dotenv

load_dotenv()
url = os.getenv("URL_SQLITE")
engine = create_async_engine(url=url)

async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(40), nullable=True)
    tg_id: Mapped[int] = mapped_column(BigInteger)
    best_cat: Mapped[str] = mapped_column(String(200), nullable=True)
    active: Mapped[str] = mapped_column(String(50), nullable=True)


class rawNews(Base):
    __tablename__ = "rawnews"

    id: Mapped[int] = mapped_column(primary_key=True)
    article: Mapped[str] = mapped_column(String(500))
    text: Mapped[str] = mapped_column(String(5000))
    collected_at: Mapped[str] = mapped_column(String(22))

class News(Base):
    __tablename__ = "news"

    id: Mapped[int] = mapped_column(primary_key=True)
    article: Mapped[str] = mapped_column(String(500))
    text: Mapped[str] = mapped_column(String(900), nullable=True)
    cat: Mapped[str] = mapped_column(String(900), nullable=True)
    mark: Mapped[int] = mapped_column(nullable=True)
    source: Mapped[str] = mapped_column(String(30))
    linkToImg: Mapped[str] = mapped_column(nullable=True)
    collected_at: Mapped[str] = mapped_column(String(22))

class Note(Base):
    __tablename__ = "notes"

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int] = mapped_column(BigInteger)
    article: Mapped[str] = mapped_column(nullable=True)
    content: Mapped[str] = mapped_column(nullable=True)
    active: Mapped[str] = mapped_column(nullable=True)

class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int] = mapped_column(BigInteger)
    content: Mapped[str] = mapped_column(nullable=True)
    collected_at: Mapped[str] = mapped_column(nullable=True)

async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
