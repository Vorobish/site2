from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy import Column, Integer, String

engine = create_engine("sqlite:///db_food.db", echo=True)

SessionLocal = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass

# pip3 install alembic
# alembic init migrations
# alembic init app.migrations   # только один раз - это создание папки
# alembic revision --autogenerate -m "Initial migration"    # создана первая миграция но ещё нет в БД
# alembic upgrade head  # загрузили в БД
