import asyncio
from datetime import datetime
from typing import Optional, Union, Dict

from fastapi import FastAPI, Query
from typer import Typer

from yadiskapi.database import init_models
# from yadiskapi.routers import users, items
from yadiskapi.config import settings
from yadiskapi.schemas import (
    Error,
    SystemItem,
    SystemItemHistoryResponse,
    SystemItemImportRequest,
)

app = FastAPI(
    title=settings.app_title,
    description=settings.app_description,
    version='1.0',
)


@app.get("/check")
def check_alive() -> Dict:
    return {
        'title': app.title,
        'version': app.version,
        'db_server_alive': False,
    }


@app.delete(
    '/delete/{id}',
    response_model=None,
    responses={'400': {'model': Error}, '404': {'model': Error}},
)
def delete_delete_id(id: str, date: datetime = ...) -> Union[None, Error]:
    pass


@app.post('/imports', response_model=None, responses={'400': {'model': Error}})
def post_imports(body: SystemItemImportRequest = None) -> Union[None, Error]:
    pass


@app.get(
    '/node/{id}/history',
    response_model=SystemItemHistoryResponse,
    responses={'400': {'model': Error}, '404': {'model': Error}},
)
def get_node_id_history(
    id: str,
    date_start: Optional[datetime] = Query(None, alias='dateStart'),
    date_end: Optional[datetime] = Query(None, alias='dateEnd'),
) -> Union[SystemItemHistoryResponse, Error]:
    pass


@app.get(
    '/nodes/{id}',
    response_model=SystemItem,
    responses={'400': {'model': Error}, '404': {'model': Error}},
)
def get_nodes_id(id: str) -> Union[SystemItem, Error]:
    pass


@app.get(
    '/updates',
    response_model=SystemItemHistoryResponse,
    responses={'400': {'model': Error}},
)
def get_updates(date: datetime) -> Union[SystemItemHistoryResponse, Error]:
    pass


cli = Typer()


@cli.command()
def init_db(drop_all: bool = False):
    asyncio.run(init_models(drop_all))
    print("DB tables created.")


if __name__ == "__main__":
    cli()
