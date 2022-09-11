from datetime import datetime
from typing import Union

from fastapi import APIRouter, Depends, HTTPException
from databases.core import Connection

from yadiskapi import schemas, crud
from yadiskapi.database import get_db_conn


router = APIRouter(tags=["Базовые задачи"])


@router.delete(
    '/delete/{id}',
    response_model=None,
    responses={'400': {'model': schemas.Error}, '404': {'model': schemas.Error}},
)
def delete_delete_id(id: str, date: datetime = ...) -> Union[None, schemas.Error]:
    pass


@router.post(
    '/imports',
    response_model=None,
    status_code=200,
    responses={'400': {'model': schemas.Error}},
)
async def post_imports(request: schemas.SystemItemImportRequest, db: Connection = Depends(get_db_conn)):
    update_date = request.updateDate
    try:
        await crud.bulk_create_items(db, request.items, update_date)
        return {"code": 200, "message": "Import was successful"}
    except Exception:
        # TODO: aiomisc log exception
        raise HTTPException(status_code=400, detail="Validation Failed")


@router.get(
    '/nodes/{id}',
    response_model=schemas.SystemItem,
    responses={
        '200': {'model': schemas.SystemItem},
        '400': {'model': schemas.Error},
        '404': {'model': schemas.Error},
    },
)
async def get_nodes_id(id: str, db: Connection = Depends(get_db_conn)) -> Union[schemas.SystemItem, schemas.Error]:
    pass
