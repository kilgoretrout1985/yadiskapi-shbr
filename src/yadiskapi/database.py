from sys import modules

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from yadiskapi.config import settings


engine = create_async_engine(
    settings.db_test_dsn if 'pytest' in modules else settings.db_dsn,
    echo=settings.db_echo_flag
)
Base = declarative_base()


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
