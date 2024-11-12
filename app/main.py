from datetime import datetime

from fastapi import FastAPI, Request, Depends, HTTPException, status, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from typing import Annotated
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import select, insert, update, delete
from sqlalchemy.orm import Session

from app.backend.dp_depends import get_db
from app.models import Menu
from app.models.user import User
from app.routers import user, menu, category
from app.routers.user import fake_hash_password, create_user, all_users
from app.schemas import UserAuth, CreateUser

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


def fake_decode_token(db: Annotated[Session, Depends(get_db)], token):
    # This doesn't provide any security at all
    # Check the next version
    users = db.scalars(select(User)).all()
    users_dict = {}
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
    user = get_user(users_dict, token)
    return user


async def get_current_user(db: Annotated[Session, Depends(get_db)], token: Annotated[str, Depends(oauth2_scheme)]):
    user = fake_decode_token(db, token)
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
async def login(db: Annotated[Session, Depends(get_db)], form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    # user_dict = fake_users_db.get(form_data.username)
    users = db.scalars(select(User)).all()
    users_dict = {}
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
    if form_data.username in users_dict.keys():
        user_dict = users_dict[form_data.username]
    else:
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
    context = {
        'request': request,
        'title': title,
        'content': content,
        # 'user': username,
    }
    return templates.TemplateResponse("base.html", context)


@app.post('/register/', status_code=status.HTTP_201_CREATED)
async def register(db: Annotated[Session, Depends(get_db)], request: Request, username_new: str
                   , password_new: str, email: str = Form()) -> HTMLResponse:
    user = db.scalars(select(User).where(User.username == username_new)).all()
    if user:
        messages = 'Данный логин уже существует'
    else:
        hashed_password = fake_hash_password(password_new)
        db.execute(insert(User).values(username=username_new,
                                       email=email,
                                       hashed_password=hashed_password,
                                       disabled=True,
                                       time_create=datetime.now(),
                                       time_update=datetime.now()))
        db.commit()
        messages = 'Успешная регистрация'
    context = {
        'request': request,
        'messages': messages,
        'username_new': username_new,
        'title': 'Регистрация',
    }
    return templates.TemplateResponse("register.html", context)


@app.get('/menu')
async def menu_str(db: Annotated[Session, Depends(get_db)], request: Request) -> HTMLResponse:
    title = 'Меню'
    menus = db.scalars(select(Menu)).all()
    context = {
        'request': request,
        'menus': menus,
        'title': title,
    }
    return templates.TemplateResponse("menu.html", context)

# @app.post('/login/', status_code=status.HTTP_201_CREATED)
# async def auth_user(request: Request, db: Annotated[Session, Depends(get_db)], username: str, password: str = Form()) -> HTMLResponse:
#     dict_token = login(db, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) # как это подменить?... form_data...


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






