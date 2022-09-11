from __future__ import annotations

from datetime import datetime
from enum import Enum, unique
from typing import List, Optional

from pydantic import BaseModel, Field, validator


@unique
class SystemItemType(Enum):
    FILE = 'FILE'
    FOLDER = 'FOLDER'


class SystemItemBase(BaseModel):
    """Виртуальная модель только для наследования"""
    id: str = Field(..., description='Уникальный идентфикатор', example='элемент_1_4')
    url: Optional[str] = Field(None, max_length=255, description='Ссылка на файл. Для папок поле равнно null.')
    parentId: Optional[str] = Field(None, description='id родительской папки', example='элемент_1_1')
    type: SystemItemType
    size: Optional[int] = Field(None, gt=0, description='Целое число, для папок поле должно содержать null.')

    class Config:
        use_enum_values = True


class SystemItemImport(SystemItemBase):
    """Модель объекта при импорте"""
    class Config:

        schema_extra = {
            "example": {
                "id": "элемент_1_4",
                "url": "/file/url1",
                "parentId": "элемент_1_1",
                "size": 234,
                "type": SystemItemType.FILE,
            }
        }


class SystemItem(SystemItemBase):
    """Модель объекта для возврата при запросе (из БД)"""
    date: datetime = Field(
        ...,
        description='Время последнего обновления элемента.',
        example='2022-05-28T21:12:01.000Z',
    )
    children: Optional[List[SystemItem]] = Field(
        None, description='Список всех дочерних элементов. Для файлов поле равно null.'
    )

    class Config:
        schema_extra = {
            "example": {
                "id": "элемент_1_2",
                "url": None,
                "type": SystemItemType.FOLDER,
                "parentId": None,
                "date": "2022-05-28T21:12:01.000Z",
                "size": 12,
                "children": [
                    {
                        "url": "/file/url1",
                        "id": "элемент_1_3",
                        "size": 4,
                        "date": "2022-05-28T21:12:01.000Z",
                        "type": SystemItemType.FILE,
                        "parentId": "элемент_1_2"
                    },
                    {
                        "type": SystemItemType.FOLDER,
                        "url": None,
                        "id": "элемент_1_1",
                        "date": "2022-05-26T21:12:01.000Z",
                        "parentId": "элемент_1_2",
                        "size": 8,
                        "children": [
                            {
                                "url": "/file/url2",
                                "id": "элемент_1_4",
                                "parentId": "элемент_1_1",
                                "date": "2022-05-26T21:12:01.000Z",
                                "size": 8,
                                "type": SystemItemType.FILE
                            }
                        ]
                    }
                ]
            }
        }


class SystemItemImportRequest(BaseModel):
    """Batch с объектами для импорта в БД"""
    items: List[SystemItemImport] = Field(..., description='Импортируемые элементы')
    updateDate: datetime = Field(
        ...,
        description='Время обновления добавляемых элементов.',
        example='2022-05-28T21:12:01.000Z',
    )

    # id каждого элемента является уникальным среди остальных элементов
    # поле id не может быть равно null
    @validator('items')
    def check_items_ids(cls, v):
        collected_ids = set()
        for item in v:
            if item.id is None:
                raise ValueError('ID of imported element can not be null.')
            if item.id in collected_ids:
                raise ValueError('ID of imported elements should be unique.')
            collected_ids.add(item.id)
        return v

    # родителем элемента может быть только папка
    @validator('items')
    def check_parent_ids(cls, v):
        file_ids = set([i.id for i in v if i.type == 'FILE'])
        for item in v:
            if item.id == item.parentId:
                raise ValueError("Item {} can't be self-parent.".format(item.id))
            if item.parentId is not None and item.parentId in file_ids:
                raise ValueError("Parent ({}) of an element ({}) can't be file.".format(item.parentId, item.id))
        return v

    # поле url при импорте папки всегда должно быть равно null
    # поле size при импорте папки всегда должно быть равно null
    @validator('items')
    def check_folder_specific(cls, v):
        for item in v:
            if item.type == 'FOLDER':
                if item.url is not None:
                    raise ValueError("url field for folder {} should be null.".format(item.id))
                if item.size is not None:
                    raise ValueError("size field for folder {} should be null.".format(item.id))
        return v

    # TODO:
    # дата обрабатывается согласно ISO 8601 (такой придерживается OpenAPI).
    # Если дата не удовлетворяет данному формату, ответом будет код 400.
    # @validator('updateDate')
    # def check_update_date(cls, v):
    #     if not check_datetime_is_iso8601(v):
    #         raise ValueError("Date must be in ISO 8601 format.")
    #     return v


class SystemItemHistoryUnit(SystemItemBase):
    date: datetime = Field(..., description='Время последнего обновления элемента.')

    class Config:
        schema_extra = {
            "example": {
                "id": "элемент_1_4",
                "url": "/file/url1",
                "date": "2022-05-28T21:12:01.000Z",
                "parentId": "элемент_1_1",
                "size": 234,
                "type": SystemItemType.FILE,
            }
        }


class SystemItemHistoryResponse(BaseModel):
    items: List[SystemItemHistoryUnit] = Field(
        default_factory=list, description='История в произвольном порядке.'
    )


class Error(BaseModel):
    code: int
    message: str
