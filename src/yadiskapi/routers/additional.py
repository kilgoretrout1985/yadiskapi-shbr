from datetime import datetime
from typing import Optional, Union

from fastapi import APIRouter, Query

from yadiskapi.schemas import (
    Error,
    SystemItemHistoryResponse,
)


router = APIRouter(tags=["Дополнительные задачи"])


@router.get(
    '/updates',
    response_model=SystemItemHistoryResponse,
    responses={'400': {'model': Error}},
)
def get_updates(date: datetime) -> Union[SystemItemHistoryResponse, Error]:
    pass


@router.get(
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
