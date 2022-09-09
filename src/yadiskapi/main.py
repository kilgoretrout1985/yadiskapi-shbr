import asyncio
from typing import Any, Dict

from fastapi import FastAPI 
from typer import Typer

from yadiskapi.database import init_models
from yadiskapi.routers import base, additional
from yadiskapi.config import settings


app = FastAPI(
    title=settings.app_title,
    description=settings.app_description,
    version='1.0',
)
app.include_router(base.router)
app.include_router(additional.router)


@app.get("/check", tags=["Сервисные endpoint"])
def check_alive() -> Dict[str, Any]:
    return {
        'title': app.title,
        'version': app.version,
        'db_server_alive': False,
    }


if __name__ == "__main__":
    cli = Typer()

    @cli.command()
    def init_db(drop_all: bool = False):
        asyncio.run(init_models(drop_all))
        print("DB tables created.")

    cli()
