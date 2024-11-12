from datetime import datetime
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.backend.dp_depends import get_db
from app.models import Menu
# from slugify import slugify
from sqlalchemy import select, insert, update, delete
from fastapi.responses import HTMLResponse

from app.schemas import CreateMenu

router = APIRouter(prefix="/menu", tags=["menu"])


@router.post("/create")
async def create_user(db: Annotated[Session, Depends(get_db)], create_menu: CreateMenu):
    db.execute(insert(Menu).values(name_food=create_menu.name_food,
                                   category_id=create_menu.category_id,
                                   weight_gr=create_menu.weight_gr,
                                   price=create_menu.price,
                                   ingredients=create_menu.ingredients,
                                   image=create_menu.image,
                                   time_create=datetime.now(),
                                   time_update=datetime.now()))
    db.commit()
    return {
        'status_code': status.HTTP_201_CREATED,
        'transaction': 'Пункт меню создан'
    }



