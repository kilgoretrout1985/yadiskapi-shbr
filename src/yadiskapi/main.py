from typing import Any, Dict

from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from yadiskapi.routers import base, additional
from yadiskapi.config import settings
from yadiskapi.database import get_db


app = FastAPI(
    title=settings.app_title,
    description=settings.app_description,
    version='1.0',
)
app.include_router(base.router)
app.include_router(additional.router)


@app.get("/check", tags=["Сервисные endpoint"])
async def check_alive(db: Session = Depends(get_db)) -> Dict[str, Any]:
    result = (await db.execute("SELECT 1 AS alive")).first()
    db_alive = bool(result[0])
    return {
        'title': app.title,
        'version': app.version,
        'db_server_alive': db_alive,
    }


if __name__ == "__main__":
    import asyncio
    from typer import Typer
    from yadiskapi.database import init_models
    # This is ugly, but I don't know how to fix this right now.
    # If you do not import all models - it will not create corresponding 
    # tables in the database.  
    from yadiskapi.models import *
    

    cli = Typer()


    @cli.command()
    def init_db(drop_all: bool = False):
        """
        cli command called directly `python main.py` to create db-tables at first run
        """
        asyncio.run(init_models(drop_all))
        print("DB tables created.")


    cli()
