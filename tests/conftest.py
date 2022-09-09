import asyncio
from typing import Generator

import pytest
from httpx import AsyncClient

from yadiskapi.main import app
from yadiskapi.database import init_models


# I do not understand this, he does:
# https://medium.com/@estretyakov/the-ultimate-async-setup-fastapi-sqlmodel-alembic-pytest-ae5cdcfed3d4
@pytest.fixture(scope="session")
def event_loop(request) -> Generator:  # noqa: indirect usage
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def async_client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture(scope="function", autouse=True)
async def set_up_db_tables():
    # set up code
    # recreate test db for each test-function, yes it's slow, but each test
    # starts with a fixed db state with all tables with 0 records each
    await init_models(delete_all=True)
    yield
    # teardown code
    pass
