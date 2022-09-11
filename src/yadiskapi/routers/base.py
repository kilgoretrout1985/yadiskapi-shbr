from datetime import datetime
from typing import Union

from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException

from yadiskapi.database import get_db
from yadiskapi import schemas, models, crud


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
async def post_imports(request: schemas.SystemItemImportRequest = None, db: Session = Depends(get_db)):
    update_date = request.updateDate
    async with db.begin():  # nested transaction
        for item in request.items:
            obj = await crud.create_item(db, item, update_date)
    return {
        "test_input": str(type(request.items[0].parentId)),
        "test_db": str(type(obj.parentId)),
    }
    
    # for item in request.items:
    #     if item.type.value == "OFFER" and isinstance(item.price, NoneType):
    #         raise HTTPException(status_code=400, detail="Validation Failed")
    #     tree.add(item.dict() | {"date": date})
    #     await add_item(session, item.id, item.name, item.type.value, item.parent_id)
    #     if item.price:
    #         await add_price_for_item(session, item.id, date, item.price)

    # return {"code": 200, "message": "The insertion or update was successful"}
    # if 0:
    #     raise HTTPException(status_code=400, detail="Validation Failed")
    # return {"message": "OK"}


@router.get(
    '/nodes/{id}',
    response_model=schemas.SystemItem,
    responses={
        '200': {'model': schemas.SystemItem},
        '400': {'model': schemas.Error}, 
        '404': {'model': schemas.Error},
    },
)
async def get_nodes_id(id: str, db: Session = Depends(get_db)) -> Union[schemas.SystemItem, schemas.Error]:
    db_item = await crud.get_item(db, item_id=id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item
