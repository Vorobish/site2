from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from typing import Annotated, Union
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy import select, insert, update, delete
from sqlalchemy.orm import Session


from app.backend.dp_depends import get_db
from app.models.user import User
from app.routers import user, menu, category
from app.routers.user import fake_hash_password, users_dict
from app.schemas import UserAuth

app = FastAPI()
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class UserInDB(UserAuth):
    hashed_password: str


def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


def fake_decode_token(token):
    # This doesn't provide any security at all
    # Check the next version
    # user = get_user(fake_users_db, token)
    user = get_user(users_dict, token)
    return user


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    user = fake_decode_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def get_current_active_user(
        current_user: Annotated[User, Depends(get_current_user)],
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@app.post("/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    # user_dict = fake_users_db.get(form_data.username)
    for i in users_dict:
        if i == form_data.username:
            user_dict = users_dict[i]
    if not user_dict:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    user = UserInDB(**user_dict)
    hashed_password = fake_hash_password(form_data.password)
    if not hashed_password == user.hashed_password:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    return {"access_token": user.username, "token_type": "bearer"}


@app.get("/users/me")
async def read_users_me(
        current_user: Annotated[User, Depends(get_current_active_user)],
):
    return current_user


@app.get('/base')
async def base(request: Request) -> HTMLResponse:
    title = 'Главная страница'
    content = 'Для выбора товаров перейдите в Меню'
    user_base = read_users_me(Annotated[User, Depends(get_current_active_user)])
    username = 'гость'
    for i in users_dict:
        if i == user_base:
            username = user_base.username
    context = {
        'request': request,
        'title': title,
        'content': content,
        'user': username,
    }
    return templates.TemplateResponse("base.html", context)


# @app.get('/menu2')
# async def menu2(request: Request) -> HTMLResponse:
#     title = 'Меню'
#     # menus = Menu.objects.all().order_by('id')
#     context = {
#         'request': request,
#         'title': title,
#         # 'page_obj': page_obj,
#         # 'k': k,
#         # 'basket_list': basket_list,
#     }
#     return templates.TemplateResponse("menu.html", context)


app.include_router(user.router)
app.include_router(menu.router)
app.include_router(category.router)

# python -m uvicorn app.main:app
# pip3 install Jinja2 --upgrade
# pip3 install fastapi-staticfiles
# pip3 install python-multipart

# alembic init app.migrations   # только один раз - это создание папки
# alembic revision --autogenerate -m "Initial migration"    # создана первая миграция но ещё нет в БД
# alembic upgrade head  # загрузили в БД
# alembic revision --autogenerate -m "Initial revision" # последующие миграции
# alembic upgrade head  # загрузили в БД
