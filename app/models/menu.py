from app.backend.db import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Numeric, DECIMAL, Text, DateTime
from sqlalchemy.orm import relationship
from app.models import category


class Menu(Base):
    '''
        Меню - товар в меню
    '''
    __tablename__ = "menus"
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True, index=True)
    name_food = Column(String)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False, index=True)
    weight_gr = Column(Integer)
    price = Column(DECIMAL)
    ingredients = Column(Text)
    image = Column(String)
    time_create = Column(DateTime)
    time_update = Column(DateTime)
    category = relationship("Category", back_populates="menus")
    orderins = relationship("OrderIn", back_populates="menu")


from sqlalchemy.schema import CreateTable

print(CreateTable(Menu.__table__))
