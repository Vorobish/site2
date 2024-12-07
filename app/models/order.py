from datetime import datetime

from app.backend.db import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Numeric, DECIMAL, Text, DateTime
from sqlalchemy.orm import relationship
from app.models import user


class Order(Base):
    '''
        Заказ
    '''
    __tablename__ = "orders"
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    summa = Column(DECIMAL, nullable=False)
    delivery = Column(String, default='self')
    phone = Column(String)
    address = Column(String)
    pay_stat = Column(String, default='not')
    status = Column(Integer, default=1)
    comment = Column(Text)
    time_create = Column(DateTime, default=datetime.now())
    time_update = Column(DateTime, default=datetime.now())

    user = relationship("User", back_populates="orders")
    orderins = relationship("OrderIn", back_populates="order")


from sqlalchemy.schema import CreateTable

print(CreateTable(Order.__table__))

# Type_delivery = [
#     ('avto', 'доставка'),
#     ('self', 'самовывоз'),
# ]
#
# Type_payment = [
#     ('paid', 'оплачен'),
#     ('part', 'аванс'),
#     ('not', 'не оплачен'),
# ]
#
# Type_status = [
#     (1, 'создан'),
#     (2, 'принят'),
#     (3, 'отказан'),
#     (4, 'в работе'),
#     (5, 'готов'),
#     (6, 'у курьера'),
#     (7, 'исполнен'),
# ]
