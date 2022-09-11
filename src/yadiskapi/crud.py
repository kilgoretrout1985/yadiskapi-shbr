from datetime import datetime
from typing import List

from aiomisc.utils import chunk_list
from databases.core import Connection

from yadiskapi import schemas


async def bulk_create_items(db: Connection, items: List[schemas.SystemItemImport], date: datetime) -> bool:
    async with db.transaction():
        # all fk constraints (including the one on parentId)
        # will be checked by postgres on commit of transaction
        # https://stackoverflow.com/a/2681413
        await db.execute("SET CONSTRAINTS ALL DEFERRED;")

        # https://stackoverflow.com/a/1109198
        # Реализуем требование openapi для /imports:
        # Элементы импортированные повторно обновляют текущие.
        # TODO: и лишь частично реализует требование
        # Изменение типа элемента с папки на файл и с файла на папку не допускается.
        query = """
            INSERT INTO items(id, url, "parentId", type, size, date)
                VALUES (:id, :url, :parentId, :type, :size, :date)
            ON CONFLICT (id) DO UPDATE
                SET url = excluded.url,
                    "parentId" = excluded."parentId",
                    size = excluded.size,
                    date = excluded.date;
        """
        for chunk in chunk_list(items, 1000):
            values = []
            for item in chunk:
                values.append({
                    'id': item.id,
                    'url': item.url,
                    'parentId': item.parentId,
                    'type': item.type,
                    'size': item.size,
                    'date': date
                })
            await db.execute_many(query=query, values=values)
    return True


async def get_item(db: Connection, item_id: str):
    pass
