from app.backend.db import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Numeric, DECIMAL, Text, DateTime
from sqlalchemy.orm import relationship
from app.models import *


class Category(Base):
    '''
        Категория товара из меню
    '''
    __tablename__ = "categories"
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True, index=True)
    name_category = Column(String)
    time_create = Column(DateTime)
    time_update = Column(DateTime)

    menus = relationship("Menu", back_populates="category")


from sqlalchemy.schema import CreateTable

print(CreateTable(Category.__table__))
