from typing import Any, Dict

from databases.core import Connection
from fastapi import FastAPI, Depends
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder
from starlette.responses import JSONResponse
from starlette import status

from yadiskapi.routers import base, additional
from yadiskapi.config import settings
from yadiskapi.database import get_db_conn, database


app = FastAPI(
    title=settings.app_title,
    description=settings.app_description,
    version='1.0',
)
app.include_router(base.router)
# app.include_router(additional.router)


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc) -> JSONResponse:
    return JSONResponse(
        # yandex openapi uses 400 instead of 422 for bad request
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": jsonable_encoder(exc.errors())},
    )


@app.get("/check", tags=["Сервисные endpoint"])
async def check_alive(db: Connection = Depends(get_db_conn)) -> Dict[str, Any]:
    result = await db.fetch_one("SELECT 1 AS alive")
    db_alive = bool(result['alive'])  # type: ignore[index]
    return {
        'title': app.title,
        'version': app.version,
        'db_server_alive': db_alive,
    }


if __name__ == "__main__":
    import asyncio
    from typer import Typer
    from yadiskapi.database import init_models

    cli = Typer()

    @cli.command()
    def init_db(drop_all: bool = False):
        """
        cli command called directly `python main.py` to create db-tables at first run
        """
        asyncio.run(init_models(drop_all))
        print("DB tables created.")

    cli()
