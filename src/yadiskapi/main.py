from typing import Any, Dict

from databases.core import Connection
from fastapi import FastAPI, Depends
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import ORJSONResponse, JSONResponse
from starlette import status

from yadiskapi.routers import base, additional
from yadiskapi.config import settings
from yadiskapi.database import get_db_conn, database
from yadiskapi import schemas


app = FastAPI(
    title=settings.app_title,
    description=settings.app_description,
    version='1.0',
    default_response_class=ORJSONResponse
)
app.include_router(base.router)
app.include_router(additional.router)


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
        # мимикрируем под стандартную ошибку валидации, но оставляем полезный текст
        content=jsonable_encoder(schemas.RichError(
            code=400,
            message="Validation Failed",
            detail=exc.errors()
        ))
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc) -> JSONResponse:
    # это нужно фактически, чтобы переименовать поле detail в json-ответе
    # (fastapi по умолчанию) в message (требование openapi проекта).
    return JSONResponse(
        status_code=exc.status_code,
        content=jsonable_encoder(schemas.Error(
            code=exc.status_code,
            message=str(exc.detail)
        ))
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
