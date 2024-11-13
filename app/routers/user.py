from datetime import datetime
from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, insert, update, delete
from sqlalchemy.orm import Session
from app.backend.dp_depends import get_db
from app.models.user import User
from app.schemas import CreateUser
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Numeric, DECIMAL, Text, DateTime

router = APIRouter(prefix="/user", tags=["user"])


@router.get("/")
async def all_users(db: Annotated[Session, Depends(get_db)]):
    users = db.scalars(select(User)).all()
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
