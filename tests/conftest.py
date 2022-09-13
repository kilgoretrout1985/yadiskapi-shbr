import asyncio
from typing import Generator

import pytest
import pytest_asyncio
from httpx import AsyncClient
from asgi_lifespan import LifespanManager

from yadiskapi.main import app
from yadiskapi.database import init_models


# требование для использования фикстур глобальнее function-scope
# https://github.com/pytest-dev/pytest-asyncio#async-fixtures
# https://medium.com/@estretyakov/the-ultimate-async-setup-fastapi-sqlmodel-alembic-pytest-ae5cdcfed3d4
@pytest.fixture(scope="session")
def event_loop(request) -> Generator:  # type: ignore[type-arg]
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def async_client():
    """
    Тестовый клиент, который может работать с приложением через asgi,
    без настоящего http-соединения

    Без lifespan в этой имитации приложения не запускается нормально БД
    https://githubmemory.com/repo/frankie567/fastapi-users/issues/361
    """
    async with LifespanManager(app):
        async with AsyncClient(app=app, base_url="http://0.0.0.0:8000") as ac:
            yield ac


@pytest_asyncio.fixture(scope="session", autouse=True)
async def set_up_db_tables():
    """
    Один раз при запуске тестов удаляет все таблицы и пересоздает их
    в тестовой БД. Эта база отдельная от основной. Настраивается в config.py
    или переменными окружения.

    Между тестами база должна сбрасываться откатами транзакции для каждой
    тест-функции.
    https://www.encode.io/databases/tests_and_migrations/#test-isolation
    """
    await init_models(delete_all=True)
    yield
