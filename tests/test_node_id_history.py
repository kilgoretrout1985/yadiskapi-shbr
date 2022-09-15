from datetime import timedelta, datetime

import pytest

from . import _give_item_import_batch, _datetime_to_string


@pytest.mark.asyncio
async def test_node_id_history_base_case(async_client):
    """Получение истории обновлений по элементу за заданный полуинтервал [from, to)."""
    batch = _give_item_import_batch(1, type="FILE")
    item = batch['items'][0]
    dt_added = batch['updateDate']
    await async_client.post("/imports", json=batch)  # add

    batch = _give_item_import_batch(0, added_timedelta=timedelta(seconds=2))
    item['size'] += 1
    batch['items'].append(item)
    dt_updated = batch['updateDate']
    await async_client.post("/imports", json=batch)  # update

    response = await async_client.get(
        "/node/{}/history".format(item['id']),
        params={'dateStart': dt_added, 'dateEnd': dt_updated}
    )
    assert response.status_code in range(200, 300)
    assert len(response.json()['items']) == 1, "Must be 1 record (initial creation), because [from, to) non-inclusive."

    response = await async_client.get("/node/{}/history".format(item['id']), params={'dateStart': dt_added})
    assert response.status_code in range(200, 300)
    assert len(response.json()['items']) == 2, "Must be full history since dateEnd omitted."

    response = await async_client.get("/node/{}/history".format(item['id']))
    assert response.status_code in range(200, 300)
    result = response.json()
    assert len(result['items']) == 2, "Must be full history since date range filters omitted."
    # SystemItemHistoryResponse не имеет порядка элементов, но изменения размера файла должно быть отражено
    assert abs(result['items'][0]['size'] - result['items'][1]['size']) == 1


@pytest.mark.asyncio
async def test_node_id_history_wrong_daterange(async_client):
    """Что будет, если dateStart > = dateEnd"""
    batch = _give_item_import_batch(1, type="FILE")
    item_id = batch['items'][0]['id']
    dt_added = batch['updateDate']
    await async_client.post("/imports", json=batch)

    response = await async_client.get(
        f"/node/{item_id}/history",
        params={'dateStart': dt_added, 'dateEnd': dt_added}
    )
    assert response.status_code == 400, "You can't have same date for from and to since half-interval is [from, to)."

    response = await async_client.get(
        f"/node/{item_id}/history",
        params={'dateStart': _datetime_to_string(datetime.now()), 'dateEnd': dt_added}
    )
    assert response.status_code == 400, "dateStart > dateEnd is not allowed."


@pytest.mark.asyncio
@pytest.mark.xfail
async def test_node_id_history_non_iso8601_date(async_client):
    """На данный момент система пропускает всё, что можно привести к datetime, надо чинить"""
    batch = _give_item_import_batch(1, type="FILE")
    item_id = batch['items'][0]['id']
    await async_client.post("/imports", json=batch)

    response = await async_client.get(
        f"/node/{item_id}/history",
        params={
            'dateStart': 13,  # this is treated like unix timestamp seconds, I guess
            'dateEnd': _datetime_to_string(datetime.now() + timedelta(seconds=1))
        }
    )
    assert response.status_code == 400
