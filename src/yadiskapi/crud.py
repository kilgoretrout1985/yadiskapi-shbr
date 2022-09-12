from datetime import datetime
from typing import Dict, List, Union

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


async def delete_item(db: Connection, item_id: str) -> int:
    # Удалением зависимых записей займется constraint ON DELETE CASCADE
    query = """
        WITH deleted AS(
            DELETE FROM items WHERE id=:id RETURNING id
        ) SELECT COUNT(*) AS cnt FROM deleted;
    """
    result = await db.fetch_one(query, values={"id": item_id})
    # в cnt считаются только удаленные нами напрямую записи, по факту получается 0 или 1
    return result['cnt']


async def get_item(db: Connection, item_id: str) -> Union[schemas.SystemItem, None]:
    query = """
        WITH RECURSIVE items_recur AS (
            SELECT * FROM items i1
                WHERE i1.id = :id
            UNION
                SELECT i2.* FROM items i2
                    INNER JOIN items_recur rec ON rec.id = i2."parentId"
        ) SELECT * FROM items_recur;
    """
    rows = await db.fetch_all(query=query, values={'id': item_id})
    if not rows:
        return None

    obj_map: Dict[str, schemas.SystemItem] = {}
    # создаем pydantic-модели для ответа (пока без детей)
    for row in rows:
        obj = schemas.SystemItem(**dict(row))
        obj_map[obj.id] = obj
    rows = None
    # формируем правильные связи children
    for _, obj in obj_map.items():
        # вторая проверка нужна, т.к. мы можем выбирать sub-tree, где у нашего
        # root-item_id есть свой родитель, которого нет в этой выборке и нет в obj_map
        if obj.parentId is not None and obj.id != item_id:
            obj_map[obj.parentId].children.append(obj)
    # возвращаем клиенту только root-элемент запроса, остальное сделает pydantic
    return obj_map[item_id]
