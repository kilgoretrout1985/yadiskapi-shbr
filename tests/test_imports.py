from typing import Dict, Union, Any
from uuid import uuid4
from datetime import datetime, timedelta
from random import randint

import pytest

from yadiskapi.schemas import datetime_from_isoformat_helper


def _give_item_import(
    type: Union[str, None] = None,
    parent_id: Union[str, None] = None
) -> Dict[str, Any]:
    """
    Создает случайные элементы для тестов. Если нужны битые данные, нужно ломать полученное.
    """
    if type is None:
        type = (['FILE', 'FOLDER'])[randint(0, 1)]
    rand_id = str(uuid4())
    return {
        "id": rand_id,
        "type": type,
        "url": None if type == 'FOLDER' else "/file/" + rand_id,
        "parentId": parent_id,
        "size": None if type == 'FOLDER' else randint(2**4, 2**31),
    }


def _give_item_import_batch(
    size: int = 0,
    type: Union[str, None] = None,
    added_timedelta: Union[timedelta, None] = None
) -> Dict[str, Any]:
    moment_in_time = datetime.now()
    if added_timedelta is not None:
        moment_in_time = moment_in_time + added_timedelta
    batch = {
        'updateDate': (moment_in_time - timedelta(days=2)).replace(microsecond=0, tzinfo=None).isoformat() + 'Z',
        'items': [_give_item_import(type=type) for _ in range(size)]
    }
    return batch


@pytest.mark.asyncio
async def test_import_base_batch(async_client):
    """Импортирует элементы файловой системы"""
    batch = _give_item_import_batch(1000)  # немного нагрузки для проверки
    response = await async_client.post("/imports", json=batch)
    assert response.status_code in range(200, 300)

    first_id = batch['items'][0]['id']
    response = await async_client.get(f"/nodes/{first_id}")
    assert response.status_code in range(200, 300)
    assert response.json()['id'] == first_id, "Nothing retrieved for imported element"


@pytest.mark.asyncio
async def test_import_change_update(async_client):
    """Элементы импортированные повторно обновляют текущие"""
    batch = _give_item_import_batch(0)
    batch['items'].append(_give_item_import(type='FILE'))
    first_id = batch['items'][0]['id']

    response = await async_client.post("/imports", json=batch)
    assert response.status_code in range(200, 300)

    batch['items'][0]['url'] += 'ADDED'
    response = await async_client.post("/imports", json=batch)
    assert response.status_code in range(200, 300)

    response = await async_client.get(f"/nodes/{first_id}")
    assert response.status_code in range(200, 300)
    assert response.json()['url'] == batch['items'][0]['url'], "URL field must update on post to /imports"


@pytest.mark.asyncio
async def test_import_no_change_type(async_client):
    """Изменение типа элемента с папки на файл и с файла на папку не допускается."""
    batch = _give_item_import_batch(0)
    batch['items'].append(_give_item_import(type='FILE'))
    batch['items'].append(_give_item_import(type='FOLDER'))
    response = await async_client.post("/imports", json=batch)
    assert response.status_code in range(200, 300)

    # try to change and post with new type
    for i in range(len(batch['items'])):
        current_id = batch['items'][i]['id']
        real_type = batch['items'][i]['type']
        # invert type
        batch['items'][i]['type'] = 'FOLDER' if real_type == 'FILE' else 'FILE'
        response = await async_client.post("/imports", json=batch)

        response = await async_client.get(f"/nodes/{current_id}")
        assert len(response.json()['type']) != real_type, "Item type changed after update"

        # восстанавливаем правильное, чтобы не мешало проверке следующего варианта
        batch['items'][i]['type'] = real_type


@pytest.mark.asyncio
async def test_import_child_before_parent(async_client):
    """Порядок элементов в запросе является произвольным."""
    batch = _give_item_import_batch(0)
    batch['items'].append(_give_item_import(type='FILE'))  # child
    batch['items'].append(_give_item_import(type='FOLDER'))  # parent
    parent_id = batch['items'][1]['id']
    batch['items'][0]['parentId'] = parent_id

    response = await async_client.post("/imports", json=batch)
    assert response.status_code in range(200, 300)

    response = await async_client.get(f"/nodes/{parent_id}")
    assert response.status_code in range(200, 300)
    assert len(response.json()['children']) == 1, "1 child should be saved"


@pytest.mark.asyncio
async def test_import_no_duplicate_id(async_client):
    """id каждого элемента является уникальным среди остальных элементов"""
    batch = _give_item_import_batch(0)
    duplicate_item = _give_item_import()
    batch['items'].append(duplicate_item)
    batch['items'].append(duplicate_item.copy())

    response = await async_client.post("/imports", json=batch)
    assert response.status_code in range(400, 500)

    response = await async_client.get(f"/nodes/{duplicate_item['id']}")
    assert response.status_code == 404, "One of duplicates added, instead of failing validation"


@pytest.mark.asyncio
async def test_import_no_null_id(async_client):
    """Поле id не может быть равно null"""
    batch = _give_item_import_batch(1)
    batch['items'][0]['id'] = None
    response = await async_client.post("/imports", json=batch)
    assert response.status_code in range(400, 500)


@pytest.mark.asyncio
async def test_import_only_folder_can_be_parent(async_client):
    """Родителем элемента может быть только папка"""
    batch = _give_item_import_batch(2, type='FILE')
    batch['items'][1]['parentId'] = batch['items'][0]['id']
    response = await async_client.post("/imports", json=batch)
    assert response.status_code in range(400, 500)


@pytest.mark.asyncio
async def test_import_parent_id_can_be_set_to_null(async_client):
    """Элементы могут не иметь родителя (при обновлении parentId на null элемент остается без родителя)"""
    batch = _give_item_import_batch(0)
    batch['items'].append(_give_item_import(type='FOLDER'))
    batch['items'].append(_give_item_import(type='FILE'))
    parent_id = batch['items'][0]['id']
    batch['items'][1]['parentId'] = parent_id

    response = await async_client.post("/imports", json=batch)
    assert response.status_code in range(200, 300)
    response = await async_client.get(f"/nodes/{parent_id}")
    assert len(response.json()['children']) == 1, "1 child should be saved"

    batch['items'][1]['parentId'] = None
    response = await async_client.post("/imports", json=batch)
    assert response.status_code in range(200, 300)
    response = await async_client.get(f"/nodes/{parent_id}")
    assert len(response.json()['children']) == 0, "0 childs should be at this point"


@pytest.mark.asyncio
async def test_import_folder_cant_have_url(async_client):
    """Поле url при импорте папки всегда должно быть равно null"""
    batch = _give_item_import_batch(1, type='FOLDER')
    batch['items'][0]['url'] = '/something/important'
    response = await async_client.post("/imports", json=batch)
    assert response.status_code in range(400, 500)


@pytest.mark.asyncio
async def test_import_folder_size_must_be_null(async_client):
    """Поле size при импорте папки всегда должно быть равно null"""
    batch = _give_item_import_batch(1, type='FOLDER')

    batch['items'][0]['size'] = 0
    response = await async_client.post("/imports", json=batch)
    assert response.status_code in range(400, 500)

    batch['items'][0]['size'] = 42
    response = await async_client.post("/imports", json=batch)
    assert response.status_code in range(400, 500)


@pytest.mark.asyncio
async def test_import_file_size_must_be_gt_zero(async_client):
    """Поле size для файлов всегда должно быть больше 0"""
    batch = _give_item_import_batch(1, type='FILE')
    batch['items'][0]['size'] = 0
    response = await async_client.post("/imports", json=batch)
    assert response.status_code in range(400, 500)


@pytest.mark.asyncio
async def test_import_file_date_must_be_updated(async_client):
    """При обновлении параметров элемента обязательно обновляется поле date в соответствии с временем обновления"""
    batch = _give_item_import_batch(1, type='FILE')
    response = await async_client.post("/imports", json=batch)
    assert response.status_code in range(200, 300)

    item = batch['items'][0]
    item['url'] = '/something'  # change something for update
    old_dt = batch['updateDate']

    batch = _give_item_import_batch(0, added_timedelta=timedelta(seconds=1))  # for new date
    batch['items'].append(item)
    response = await async_client.post("/imports", json=batch)
    assert response.status_code in range(200, 300)

    response = await async_client.get(f"/nodes/{batch['items'][0]['id']}")
    new_dt = response.json()['date']
    assert datetime_from_isoformat_helper(old_dt) < datetime_from_isoformat_helper(new_dt)


@pytest.mark.asyncio
async def test_import_folder_date_size_must_be_updated(async_client):
    """Когда добавляют файл в старую папку и она меняет свою дату на дату добавления файла и увеличивает размер"""
    batch = _give_item_import_batch(2, type='FOLDER')
    top_folder_id = batch['items'][0]['id']
    second_folder_id = batch['items'][1]['id']
    old_dt = batch['updateDate']
    batch['items'][1]['parentId'] = top_folder_id  # /top_folder/second_folder
    response = await async_client.post("/imports", json=batch)
    assert response.status_code in range(200, 300)

    batch = _give_item_import_batch(1, type='FILE', added_timedelta=timedelta(seconds=1))
    batch['items'][0]['parentId'] = second_folder_id  # /top_folder/second_folder/file
    response = await async_client.post("/imports", json=batch)
    assert response.status_code in range(200, 300)

    response = await async_client.get(f"/nodes/{top_folder_id}")
    assert response.status_code in range(200, 300)
    new_dt = response.json()['date']
    second_folder_dt = response.json()['children'][0]['date']
    assert datetime_from_isoformat_helper(old_dt) < datetime_from_isoformat_helper(new_dt)
    assert datetime_from_isoformat_helper(old_dt) < datetime_from_isoformat_helper(second_folder_dt)
    assert new_dt == second_folder_dt
    assert response.json()['size'] > 0
    assert response.json()['size'] == response.json()['children'][0]['size']
