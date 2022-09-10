from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class SystemItemType(Enum):
    FILE = 'FILE'
    FOLDER = 'FOLDER'


class SystemItemBase(BaseModel):
    """Виртуальная модель только для наследования"""
    id: str = Field(..., description='Уникальный идентфикатор', example='элемент_1_4')
    url: Optional[str] = Field(None, description='Ссылка на файл. Для папок поле равнно null.')
    parentId: Optional[str] = Field(None, description='id родительской папки', example='элемент_1_1')
    type: SystemItemType
    size: Optional[int] = Field(None, description='Целое число, для папок поле должно содержать null.')


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
    date: datetime = Field(...,
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


class SystemItemHistoryUnit(SystemItemBase):
    date: datetime = Field(..., description='Время последнего обновления элемента.')


class SystemItemHistoryResponse(BaseModel):
    items: Optional[List[SystemItemHistoryUnit]] = Field(
        None, description='История в произвольном порядке.'
    )


class Error(BaseModel):
    code: int
    message: str
