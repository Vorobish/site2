from datetime import datetime

from app.backend.db import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Numeric, DECIMAL, Text, DateTime
from sqlalchemy.orm import relationship
from app.models import user
from app.models import order


class OrderIn(Base):
    __tablename__ = "orderins"
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)
    menu_id = Column(Integer, ForeignKey("menus.id"), nullable=False, index=True)
    count = Column(Integer)
    summa = Column(DECIMAL)
    time_create = Column(DateTime, default=datetime.now())
    time_update = Column(DateTime, default=datetime.now())
    order = relationship("Order", back_populates="orderins")
    menu = relationship("Menu", back_populates="orderins")


from sqlalchemy.schema import CreateTable
print(CreateTable(OrderIn.__table__))