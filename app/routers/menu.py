from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
# from slugify import slugify
# from sqlalchemy import select, insert, update, delete
# from sqlalchemy.orm import Session
#
# from app.backend.db_depends import get_db
# from app.models import Task, User
# from app.schemas import CreateTask, UpdateTask

router = APIRouter(prefix="/menu", tags=["menu"])


# @router.get("/")
# async def all_menu(db: Annotated[Session, Depends(get_db)]):
#     tasks = db.scalars(select(Task)).all()
#     return tasks


