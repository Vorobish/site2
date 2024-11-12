from datetime import datetime
from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, status
from slugify import slugify
from sqlalchemy import select, insert, update, delete
from sqlalchemy.orm import Session

from app.backend.dp_depends import get_db
from app.models.user import User
from app.schemas import CreateUser  # , UpdateUser

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Numeric, DECIMAL, Text, DateTime


router = APIRouter(prefix="/user", tags=["user"])


# @router.get("/")
# async def welcome() -> dict:
#     return {"message": "Hi"}

# result = []

users_dict = {}


@router.get("/")
async def all_users(db: Annotated[Session, Depends(get_db)]):
    global users_dict
    users = db.scalars(select(User)).all()
    for i in users:
        users_dict.update({
                i.username: {
                    "username": i.username,
                    "full_name": i.full_name,
                    "email": i.email,
                    "hashed_password": i.hashed_password,
                    "disabled": i.disabled,
                }
            })
    return users

# @router.get("/user_id")
# async def user_by_id(db: Annotated[Session, Depends(get_db)], user_id: int):
#     user = db.scalars(select(User).where(User.id == user_id)).all()
#     if len(user) == 0:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail='User was not found'
#         )
#     else:
#         return user


@router.post("/create")
async def create_user(db: Annotated[Session, Depends(get_db)], create_user: CreateUser):
    user_exists = db.scalar(select(User).where(User.username == create_user.username))
    # result = [r.id for r in db.query(User.id)]
    # print(result)
    if user_exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Пользователь с таким логином уже существует'
            )
    hashed_password = fake_hash_password(create_user.password)
    db.execute(insert(User).values(username=create_user.username,
                                   email=create_user.email,
                                   hashed_password=hashed_password,
                                   disabled=create_user.disabled,
                                   time_create=datetime.now(),
                                   time_update=datetime.now()))
    db.commit()
    return {
        'status_code': status.HTTP_201_CREATED,
        'transaction': 'Пользователь создан'
    }


def fake_hash_password(password: str):
    return "fakehashed" + password

# pip install python-slugify


# @router.put("/update")
# async def update_user(db: Annotated[Session, Depends(get_db)], user_id: int, update_user: UpdateUser):
#     user = db.scalar(select(User).where(User.id == user_id))
#     if user is None:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail='User was not found'
#         )
#
#     db.execute(update(User).where(User.id == user_id).values(
#         firstname=update_user.firstname,
#         lastname=update_user.lastname,
#         age=update_user.age))
#
#     db.commit()
#     return {
#         'status_code': status.HTTP_200_OK,
#         'transaction': 'User update is successful!'
#     }


# @router.get("/user_id/tasks")
# async def tasks_by_user_id(db: Annotated[Session, Depends(get_db)], user_id: int):
#     user = db.scalar(select(User).where(User.id == user_id))
#     if user is None:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail='User was not found'
#         )
#     task = db.scalar(select(Task).where(Task.user_id == user_id))
#     if task is None:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail='Tasks was not found'
#         )
#     return task
