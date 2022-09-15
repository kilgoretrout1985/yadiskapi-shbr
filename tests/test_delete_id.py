from datetime import datetime, timedelta

import pytest

from . import _give_2_folder_tree_import_batch, _give_item_import_batch, _datetime_to_string


# для выполнения запросов на удаления нужна дата-время, вычитаем день
# т.к. за часовыми поясами не следим, чтобы дата не оказалась в будущем
TEST_DATE_QS = {'date': _datetime_to_string(datetime.now() - timedelta(days=1))}


@pytest.mark.asyncio
async def test_delete_base_case(async_client):
    """Удалить элемент по идентификатору"""
    batch = _give_item_import_batch(size=1)
    item_id = batch['items'][0]['id']
    await async_client.post("/imports", json=batch)

    response = await async_client.delete(f"/delete/{item_id}", params=TEST_DATE_QS)
    assert response.status_code in range(200, 300)

    response = await async_client.get(f"nodes/{item_id}")
    assert response.status_code == 404

    response = await async_client.delete(f"/delete/{item_id}", params=TEST_DATE_QS)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_root_folder(async_client):
    """При удалении папки удаляются все дочерние элементы."""
    # /fld1/fld2/file1,file2
    batch = _give_2_folder_tree_import_batch(files_num=2)
    root_folder_id = batch['items'][0]['id']
    await async_client.post("/imports", json=batch)

    response = await async_client.delete(f"/delete/{root_folder_id}", params=TEST_DATE_QS)
    assert response.status_code in range(200, 300)

    for i in range(len(batch['items'])):
        item_id = batch['items'][i]['id']
        response = await async_client.get(f"/nodes/{item_id}")
        assert response.status_code == 404


async def test_delete_date_in_query_required(async_client):
    """Параметр date в запросе на удаление обязателен."""
    batch = _give_item_import_batch(size=1)
    item_id = batch['items'][0]['id']
    await async_client.post("/imports", json=batch)

    response = await async_client.delete(f"/delete/{item_id}")  # no date
    assert response.status_code in range(400, 500)
    response = await async_client.delete(f"/delete/{item_id}", params={'date': 'lol'})
    assert response.status_code in range(400, 500)

    response = await async_client.get(f"/nodes/{item_id}")
    assert response.status_code in range(200, 300), "Item should be available since deletion failed."
