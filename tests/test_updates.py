from datetime import timedelta
import pytest

from yadiskapi.schemas import datetime_from_isoformat_helper

from . import _give_2_folder_tree_import_batch, _give_item_import_batch


@pytest.mark.asyncio
async def test_updates_base_case(async_client):
    """
    Получение списка **файлов**, которые были обновлены за последние 24 часа
    включительно [date - 24h, date] от времени переданном в запросе.
    """
    batch = _give_2_folder_tree_import_batch(files_num=2)
    # 2 files + 2 folders = 4 items added total (+4 records in items_history table)
    dt_added = batch['updateDate']

    await async_client.post("/imports", json=batch)

    response = await async_client.get("/updates", params={'date': dt_added})
    assert response.status_code in range(200, 300)
    assert len(response.json()['items']) == 2, "Must show only file-updates, not folders."

    dt_too_old = datetime_from_isoformat_helper(dt_added) - timedelta(days=2)
    response = await async_client.get("/updates", params={'date': dt_too_old})
    # 404 для пустого ответа в этом endpoint не предусмотрен, только 200 и 400
    assert len(response.json()['items']) == 0


@pytest.mark.asyncio
@pytest.mark.xfail
async def test_updates_non_iso8601_date(async_client):
    """На данный момент система пропускает всё, что можно привести к datetime, надо чинить"""
    await async_client.post("/imports", json=_give_item_import_batch(1, type="FILE"))
    response = await async_client.get("/updates", params={'date': 13})
    assert response.status_code == 400
