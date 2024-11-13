from datetime import datetime
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.backend.dp_depends import get_db
from app.models import Category
from sqlalchemy import select, insert, update, delete
from app.schemas import CreateCategory

router = APIRouter(prefix="/category", tags=["category"])


@router.get("/")
async def all_category(db: Annotated[Session, Depends(get_db)]):
    categories = db.scalars(select(Category)).all()
    return categories


@router.post("/create")
async def create_category(db: Annotated[Session, Depends(get_db)], create_category: CreateCategory):
    category_exists = db.scalar(select(Category).where(Category.name_category == create_category.name_category))
    if category_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Данная категория еды уже существует'
        )
    db.execute(insert(Category).values(name_category=create_category.name_category,
                                       time_create=datetime.now(),
                                       time_update=datetime.now()))
    db.commit()
    return {
        'status_code': status.HTTP_201_CREATED,
        'transaction': 'Категория создана'
    }
