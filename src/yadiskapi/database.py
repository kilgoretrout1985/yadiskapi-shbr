from sys import modules

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import (
    Column, DateTime, Enum as PgEnum, ForeignKey, String, Table, 
    BigInteger
)

from yadiskapi.config import settings
from yadiskapi.schemas import SystemItemType


engine = create_async_engine(
    settings.db_test_dsn if 'pytest' in modules else settings.db_dsn,
    echo=settings.db_echo_flag
)
Base = declarative_base()


items_table = Table(
    'items',
    Base.metadata,
    Column('id', String, primary_key=True, autoincrement=False),
    Column('url', String(255), nullable=True),
    Column('parentId', String, ForeignKey('items.id', ondelete='CASCADE'), nullable=True),
    Column('type', PgEnum(SystemItemType, name='type'), nullable=False),    
    Column('size', BigInteger, nullable=True),
    Column('date', DateTime, nullable=False)
)


async_session = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    class_=AsyncSession,
    # in async settings we don't want SQLAlchemy to issue new SQL queries
    # to the database when accessing already commited objects.
    expire_on_commit=False
)


async def get_db() -> AsyncSession:
    async with async_session() as db:
        yield db


async def init_models(delete_all=False):
    async with engine.begin() as conn:
        if delete_all:
            await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


if __name__ == "__main__":
    # this shows CREATE TABLE sql without running it for debug purposes
    from sqlalchemy.schema import CreateTable
    print(CreateTable(items_table))
