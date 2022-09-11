from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession, AsyncResult
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload, joinedload, subqueryload

from yadiskapi import models, schemas


async def create_item(db: AsyncSession, posted_item: schemas.SystemItemImport, date: datetime) -> models.Item:
    db_item = models.Item(date=date, **posted_item.dict())
    db.add(db_item)
    # await db.commit()
    # this commented line breaks everything because of .items relationship
    # https://docs.sqlalchemy.org/en/14/orm/extensions/asyncio.html#preventing-implicit-io-when-using-asyncsession
    # await db.refresh(db_user, attribute_names=['id', 'items'])
    return db_item


async def get_item(db: AsyncSession, item_id: str) -> models.Item:
    results: AsyncResult = await db.execute(
        # selectinload because no lasy loading is allowed in async mode
        select(models.Item).where(models.Item.id == item_id).options(joinedload(models.Item.children))
    )
    return results.scalars().unique().one()


