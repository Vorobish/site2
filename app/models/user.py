from app.backend.db import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Numeric, DECIMAL, Text, DateTime
from sqlalchemy.orm import relationship
# from app.models import *


class User(Base):
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String)
    full_name = Column(String)
    email = Column(String)
    hashed_password = Column(String)
    disabled = Column(Boolean, default=False)
    time_create = Column(DateTime)
    time_update = Column(DateTime)

    orders = relationship("Order", back_populates="user")


from sqlalchemy.schema import CreateTable
print(CreateTable(User.__table__))





