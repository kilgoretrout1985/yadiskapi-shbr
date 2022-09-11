from sys import modules

from databases import Database
from databases.core import Connection
import asyncpg.exceptions

from yadiskapi.config import settings


# https://www.encode.io/databases/
database = Database(
    settings.db_test_dsn if 'pytest' in modules else settings.db_dsn,
    # TODO: tweak this pool settings and check that they correspond to pg docker container settings
    min_size=2,
    max_size=5
)


async def get_db_conn() -> Connection:  # type: ignore[misc]
    async with database.connection() as db_con:
        yield db_con


async def init_models(delete_all=False):
    await database.connect()
    async with database.connection() as conn:
        if delete_all:
            await conn.execute(query="DROP TABLE IF EXISTS items;")
            await conn.execute(query="DROP TYPE IF EXISTS type;")

        # опции IF NOT EXISTS нет при создании типов, поэтому просто пытаемся
        # создать во вложенной транзакции и откатываем, если такой тип уже есть
        transaction = await conn.transaction()
        try:
            query = """CREATE TYPE type AS ENUM ('FILE', 'FOLDER');"""
            await conn.execute(query=query)
        except asyncpg.exceptions.DuplicateObjectError:
            await transaction.rollback()
        else:
            await transaction.commit()

        query = """
            CREATE TABLE IF NOT EXISTS items
            (
                id character varying COLLATE pg_catalog."default" NOT NULL,
                url character varying(255) COLLATE pg_catalog."default",
                "parentId" character varying COLLATE pg_catalog."default",
                type type NOT NULL,
                size bigint,
                date timestamp with time zone NOT NULL,
                CONSTRAINT items_pkey PRIMARY KEY (id),
                CONSTRAINT "items_parentId_fkey" FOREIGN KEY ("parentId")
                    REFERENCES items (id) MATCH SIMPLE
                    ON UPDATE NO ACTION
                    ON DELETE CASCADE
                    DEFERRABLE INITIALLY IMMEDIATE
            );
        """
        await database.execute(query=query)
    await database.disconnect()
