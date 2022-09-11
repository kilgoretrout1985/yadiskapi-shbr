from sqlalchemy.orm import relationship
from sqlalchemy import (
    Column, DateTime, Enum as PgEnum, ForeignKey, String, BigInteger
)

from yadiskapi.database import Base
from yadiskapi.schemas import SystemItemType


class Item(Base):
    __tablename__ = "items"

    id = Column(String, primary_key=True, autoincrement=False)
    url = Column(String(255), nullable=True)
    parentId = Column(String, ForeignKey('items.id', ondelete='CASCADE'), nullable=True)
    type = Column(PgEnum(SystemItemType, name='type'), nullable=False) 
    size = Column(BigInteger, nullable=True)
    date = Column(DateTime(timezone=True), nullable=False)
    # https://docs.sqlalchemy.org/en/14/orm/self_referential.html
    # the relationship is is assumed by default to be one-to-many
    children = relationship("Item")

    __mapper_args__ = {"eager_defaults": True}
