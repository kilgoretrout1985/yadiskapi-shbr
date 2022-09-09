from datetime import datetime
from typing import Union

from fastapi import APIRouter

from yadiskapi.schemas import (
    Error,
    SystemItem,
    SystemItemImportRequest,
)


router = APIRouter(tags=["Базовые задачи"])


@router.delete(
    '/delete/{id}',
    response_model=None,
    responses={'400': {'model': Error}, '404': {'model': Error}},
)
def delete_delete_id(id: str, date: datetime = ...) -> Union[None, Error]:
    pass


@router.post('/imports', response_model=None, responses={'400': {'model': Error}})
def post_imports(body: SystemItemImportRequest = None) -> Union[None, Error]:
    pass


@router.get(
    '/nodes/{id}',
    response_model=SystemItem,
    responses={'400': {'model': Error}, '404': {'model': Error}},
)
def get_nodes_id(id: str) -> Union[SystemItem, Error]:
    pass
