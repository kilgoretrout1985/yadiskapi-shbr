from typing import Dict, Union, Any
from datetime import datetime, timedelta
from random import randint
from uuid import uuid4


def _datetime_to_string(dt: datetime) -> str:
    return dt.replace(microsecond=0, tzinfo=None).isoformat() + 'Z'


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
    parent_id: Union[str, None] = None,
    added_timedelta: Union[timedelta, None] = None
) -> Dict[str, Any]:
    moment_in_time = datetime.now()
    if added_timedelta is not None:
        moment_in_time = moment_in_time + added_timedelta
    batch = {
        'updateDate': _datetime_to_string(moment_in_time - timedelta(days=2)),
        'items': [_give_item_import(type=type, parent_id=parent_id) for _ in range(size)]
    }
    return batch


def _give_2_folder_tree_import_batch(files_num: int = 1):
    """Хелпер, который возвращает дерево /parent_folder/second_folder/file1..files_num"""
    batch = _give_item_import_batch(1, type='FOLDER')
    parent_id = batch['items'][0]['id']
    batch['items'].append(_give_item_import(type='FOLDER', parent_id=parent_id))
    second_id = batch['items'][1]['id']
    for _ in range(files_num):
        batch['items'].append(_give_item_import(type='FILE', parent_id=second_id))
    return batch
