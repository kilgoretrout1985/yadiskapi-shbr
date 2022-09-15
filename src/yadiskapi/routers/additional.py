from datetime import datetime, timedelta
from typing import Optional, Union

from fastapi import APIRouter, Query, Depends, HTTPException
from fastapi.responses import ORJSONResponse
from databases.core import Connection

from yadiskapi import schemas, crud
from yadiskapi.database import get_db_conn


router = APIRouter(
    tags=["Дополнительные задачи"],
    default_response_class=ORJSONResponse
)


@router.get(
    '/updates',
    status_code=200,
    response_model=schemas.SystemItemHistoryResponse,
    responses={
        '200': {
            'model': schemas.SystemItemHistoryResponse,
            'description': 'Информация об элементе.'
        },
        '400': {
            'model': schemas.Error,
            'description': 'Невалидная схема документа или входные данные не верны.'
        }
    }
)
async def get_updates(
    date: datetime, db: Connection = Depends(get_db_conn)
) -> Union[schemas.SystemItemHistoryResponse, schemas.Error]:
    history_response = await crud.get_history_daterange(db, date - timedelta(hours=24), date)
    return history_response


@router.get(
    '/node/{id}/history',
    status_code=200,
    response_model=schemas.SystemItemHistoryResponse,
    responses={
        '200': {
            'model': schemas.SystemItemHistoryResponse,
            'description': 'История по элементу.'
        },
        '400': {
            'model': schemas.Error,
            'description': 'Некорректный формат запроса или некорректные даты интервала.'
        },
        '404': {
            'model': schemas.Error,
            'description': 'Элемент не найден.'
        }
    },
)
async def get_node_id_history(
    id: str,
    date_start: Optional[datetime] = Query(None, alias='dateStart'),
    date_end: Optional[datetime] = Query(None, alias='dateEnd'),
    db: Connection = Depends(get_db_conn)
) -> Union[schemas.SystemItemHistoryResponse, schemas.Error]:
    if date_start and date_end and date_start >= date_end:
        raise HTTPException(status_code=400, detail="Validation Failed")

    history_response = await crud.get_item_history(db, id, date_start, date_end)
    if len(history_response.items) == 0:
        raise HTTPException(status_code=404, detail="Item not found")

    return history_response
