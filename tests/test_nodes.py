import pytest

from . import _give_2_folder_tree_import_batch, _give_item_import_batch


@pytest.mark.asyncio
async def test_nodes_base_read(async_client):
    """
    Получить информацию об элементе по идентификатору. При получении 
    информации о папке также предоставляется информация о её дочерних элементах.
    """
    # /fld1/fld2/file1
    batch = _give_2_folder_tree_import_batch(files_num=1)
    await async_client.post("/imports", json=batch)
    response = await async_client.get("/nodes/{}".format(batch['items'][0]['id']))
    assert response.status_code in range(200, 300)
    data = response.json()
    assert len(data['children']) == 1, "fld1 has no link to fld2"
    assert len(data['children'][0]['children']) == 1, "fld2 has no link to file1"
    assert data['children'][0]['children'][0]['type'] == 'FILE'


@pytest.mark.asyncio
async def test_nodes_different_children_representation(async_client):
    """Для пустой папки поле children равно пустому массиву, а для файла равно null"""
    batch = _give_item_import_batch(1, type='FOLDER')
    await async_client.post("/imports", json=batch)
    response = await async_client.get("/nodes/{}".format(batch['items'][0]['id']))
    assert response.status_code in range(200, 300)
    assert response.json()['children'] == []

    batch = _give_item_import_batch(1, type='FILE')
    await async_client.post("/imports", json=batch)
    response = await async_client.get("/nodes/{}".format(batch['items'][0]['id']))
    assert response.status_code in range(200, 300)
    assert response.json()['children'] == None


@pytest.mark.asyncio
async def test_nodes_folder_size(async_client):
    """
    Размер папки - это суммарный размер всех её элементов. 
    Если папка не содержит элементов, то размер равен 0.
    """
    batch = _give_item_import_batch(1, type='FOLDER')
    await async_client.post("/imports", json=batch)
    folder_id = batch['items'][0]['id']
    folder_size = 0
    
    response = await async_client.get("/nodes/{}".format(folder_id))
    assert response.json()['size'] == folder_size, "Empty folder must have size 0"

    for _ in range(2):
        await async_client.post(
            "/imports", 
            json=_give_item_import_batch(1, type='FILE', parent_id=folder_id)
        )
        response = await async_client.get("/nodes/{}".format(folder_id))
        assert response.json()['size'] > folder_size, "Added file must increase folder size"
        folder_size += response.json()['size']
    

@pytest.mark.asyncio
async def test_nodes_folder_size_change_on_file_size_change(async_client):
    """При обновлении размера элемента, суммарный размер папки, которая содержит этот элемент, тоже обновляется."""
    batch = _give_2_folder_tree_import_batch(files_num=1)
    folder_id = batch['items'][0]['id']
    file_size_initial = batch['items'][2]['size']
    await async_client.post("/imports", json=batch)  # 1st post
    batch['items'][2]['size'] += 2
    file_size_actual = batch['items'][2]['size']
    await async_client.post("/imports", json=batch)  # update

    response = await async_client.get("/nodes/{}".format(folder_id))
    assert file_size_initial != file_size_actual
    assert response.json()['size'] != file_size_initial
    assert response.json()['size'] == file_size_actual

