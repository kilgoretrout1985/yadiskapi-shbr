from typing import Union
from sys import modules

from databases import Database
from databases.core import Connection
import asyncpg.exceptions

from yadiskapi.config import settings


# https://www.encode.io/databases/
def configure_database(my_force_rollback: Union[None, bool] = None) -> Database:
    """
    Хелпер для создания конфигурации БД. Нужен, т.к. есть 3 варианта использования:
    1) к реальной БД, не использует принудительный откат транзакций в конце,
    2) к тестовой БД во время тестов - использует,
    3) к тестовой БД для первоначального создания таблиц перед тестами - НЕ использует.
    """
    if my_force_rollback is not None:
        force_rollback = my_force_rollback
    else:
        force_rollback = True if 'pytest' in modules else False

    return Database(
        settings.db_test_dsn if 'pytest' in modules else settings.db_dsn,
        force_rollback=force_rollback,
        # TODO: tweak this pool settings and check that they correspond to pg docker container settings
        min_size=2,
        max_size=5
    )


database = configure_database()


async def get_db_conn() -> Connection:  # type: ignore[misc]
    async with database.connection() as db_con:
        yield db_con


async def init_models(delete_all=False):
    """
    Функция для создания (и опциально для удаления старых) таблиц приложения
    в тестовой и обычной БД. Вызывается: 1) из консольной команде перед запуском
    веб-сервера, 2) из фикстуры pytest один раз перед запуском тестов.

    Использует отдельный коннект к базе, чтобы даже из тестовой среды обойти
    ограничение на откат всех транзакций в конце соединения.
    """
    one_time_db_conn = configure_database(my_force_rollback=False)
    await one_time_db_conn.connect()
    async with one_time_db_conn.connection() as conn:
        async with conn.transaction():
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
                    id character varying NOT NULL,
                    url character varying(255),
                    "parentId" character varying,
                    type type NOT NULL,
                    size bigint,
                    date timestamp with time zone NOT NULL,
                    CONSTRAINT items_pkey PRIMARY KEY (id),
                    CONSTRAINT "items_parentId_fkey" FOREIGN KEY ("parentId")
                        REFERENCES items (id) MATCH SIMPLE
                        ON UPDATE CASCADE
                        ON DELETE CASCADE
                        DEFERRABLE INITIALLY IMMEDIATE
                );
            """
            await one_time_db_conn.execute(query=query)
            query = """CREATE INDEX IF NOT EXISTS items_parentId_fkey_idx ON items ("parentId");"""
            await one_time_db_conn.execute(query=query)
    await one_time_db_conn.disconnect()
