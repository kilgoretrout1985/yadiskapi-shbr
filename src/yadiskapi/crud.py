from datetime import datetime
from typing import Dict, List, Union

from aiomisc.utils import chunk_list
from databases.core import Connection

from yadiskapi import schemas


async def _folders_recount_stat(db: Connection) -> None:
    """Пересчитываем размеры папок и их даты после добавления и удаления элементов"""
    async with db.transaction():
        query = """
            WITH RECURSIVE cte AS (
                SELECT id, "parentId", type, date,
                       CASE WHEN type='FILE' THEN size ELSE 0 END AS size
                    FROM items
                UNION ALL
                SELECT i2.id, i2."parentId", i2.type, GREATEST(cte.date, i2.date) as date,
                       CASE WHEN i2.type='FILE' THEN i2.size + cte.size ELSE cte.size END AS size
                    FROM cte
                        INNER JOIN items i2 ON cte."parentId" = i2.id
            )
            SELECT id, "parentId", type, SUM(size) as new_size, MAX(date) as new_date
                FROM cte
                GROUP BY id, "parentId", type
                HAVING cte.type = 'FOLDER';
        """
        # я не смог вытащить эти данные сразу в update, приходится пропускать
        # через python
        rows = await db.fetch_all(query=query)
        values_all = []
        for row in rows:
            values_all.append({
                'id': row['id'],
                'new_size': int(row['new_size']),
                'new_date': row['new_date']
            })

        for chunk in chunk_list(values_all, 1000):
            query = "UPDATE items SET size=CAST(:new_size AS BIGINT), date=:new_date WHERE id=:id;"
            await db.execute_many(query=query, values=chunk)


async def bulk_create_items(db: Connection, items: List[schemas.SystemItemImport], date: datetime) -> bool:
    async with db.transaction():
        # all fk constraints (including the one on parentId)
        # will be checked by postgres on commit of transaction
        # https://stackoverflow.com/a/2681413
        await db.execute("SET CONSTRAINTS ALL DEFERRED;")

        # https://stackoverflow.com/a/1109198
        # Реализуем требование openapi для /imports:
        # Элементы импортированные повторно обновляют текущие.
        #
        # COALESCE тк при импорте папок size обязательно null и это надо валидировать,
        # а потом во всех моделях, читаемых из БД, уже обязательно 0+
        query = """
            INSERT INTO items(id, url, "parentId", type, size, date)
                VALUES (:id, :url, :parentId, :type, COALESCE(CAST(:size AS BIGINT), 0), :date)
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

    # вышли из транзакции, чтобы Postgres проверил дубликаты и валидность ключей
    # т.к. нет смысла пересчитывать статистику, если все сломалось
    await _folders_recount_stat(db)

    return True


async def delete_item(db: Connection, item_id: str) -> int:
    async with db.transaction():
        # Удалением зависимых записей займется constraint ON DELETE CASCADE
        query = """
            WITH deleted AS(
                DELETE FROM items WHERE id=:id RETURNING id
            ) SELECT COUNT(*) AS cnt FROM deleted;
        """
        result = await db.fetch_one(query, values={"id": item_id})
        await _folders_recount_stat(db)
        # в cnt считаются только удаленные нами напрямую записи, по факту получается 0 или 1
        return result['cnt']  # type: ignore[no-any-return, index]


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

    # формируем правильные связи children
    for _, obj in obj_map.items():
        # вторая проверка нужна, т.к. мы можем выбирать sub-tree, где у нашего
        # root-item_id есть свой родитель, которого нет в этой выборке и нет в obj_map
        if obj.parentId is not None and obj.id != item_id:
            obj_map[obj.parentId].children.append(obj)  # type: ignore[union-attr]
    # возвращаем клиенту только root-элемент запроса, остальное сделает pydantic
    return obj_map[item_id]
