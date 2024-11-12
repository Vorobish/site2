from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.backend.dp_depends import get_db
from app.models import Category

# from slugify import slugify
from sqlalchemy import select, insert, update, delete

router = APIRouter(prefix="/category", tags=["category"])


@router.get("/")
async def all_category(db: Annotated[Session, Depends(get_db)]):
    categories = db.scalars(select(Category)).all()
    return categories


# 2024-11-08 20:34:41	1	Пицца	FoodProject\static\vegan1.jpg	2024-11-08 20:34:49.570500
# 2024-11-08 20:36:35	2	Напитки	FoodProject\static\mors1.webp	2024-11-08 20:36:36.951563


