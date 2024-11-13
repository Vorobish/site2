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

user_id_current = 0
username_current = 'гость'
basket_list = {1: 3, 2: 2}

# Авторизация в части Auth2


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
async def login(request: Request, db: Annotated[Session, Depends(get_db)]
                , form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> HTMLResponse:
    global user_id_current, username_current
    users = db.scalars(select(User)).all()
    users_dict = {}
    for i in users:
        users_dict.update({
                i.username: {
                    "id": i.id,
                    "username": i.username,
                    "full_name": i.full_name,
                    "email": i.email,
                    "hashed_password": i.hashed_password,
                    "disabled": i.disabled,
                }
            })
    if form_data.username in users_dict.keys():
        user_dict = users_dict[form_data.username]
        id = user_dict['id']
    else:
        # raise HTTPException(status_code=400, detail="Некорректный логин или пароль")
        context = {
            'request': request,
            'title': 'Авторизация',
            'messages': 'Некорректный логин или пароль',
        }
        return templates.TemplateResponse("login.html", context)
    user = UserInDB(**user_dict)
    hashed_password = fake_hash_password(form_data.password)
    if not hashed_password == user.hashed_password:
        # raise HTTPException(status_code=400, detail="Некорректный логин или пароль")
        context = {
            'request': request,
            'title': 'Авторизация',
            'messages': 'Некорректный логин или пароль',
        }
        return templates.TemplateResponse("login.html", context)
    user_id_current = id
    username_current = user.username
    context = {
        'request': request,
        'title': 'Авторизация',
        "access_token": user.username,
        "token_type": "bearer",
        'messages': f'Успешная авторизация (пользователь: {user.username})',
        'username_current': username_current,
        'user_id': user_id_current,
    }
    return templates.TemplateResponse("login.html", context)
    # return {"access_token": user.username, "token_type": "bearer"}


async def read_users_me(
        current_user: Annotated[User, Depends(get_current_active_user)],
):
    return current_user


# Главная страница

@app.get('/base')
async def base(request: Request) -> HTMLResponse:
    global user_id_current, username_current
    title = 'Главная страница'
    content = 'Для выбора товаров перейдите в Меню'
    context = {
        'request': request,
        'title': title,
        'content': content,
        'username_current': username_current,
        'user_id': user_id_current,
    }
    return templates.TemplateResponse("base.html", context)


# Регистрация

@app.get("/register/")
async def register(request: Request):
    global user_id_current, username_current
    context = {
        'request': request,
        'title': 'Регистрация',
        'username_current': username_current,
        'user_id': user_id_current,
    }
    return templates.TemplateResponse("register.html", context)


@app.post("/register_post/")
async def register_post(request: Request, db: Annotated[Session, Depends(get_db)], username_new: str = Form(),
                        password_new: str = Form(), email_new: str = Form()) -> HTMLResponse:
    global user_id_current, username_current
    messages = ''
    user = db.scalars(select(User).where(User.username == username_new)).first()
    if user:
        messages = 'Данный логин уже существует'
    else:
        hashed_password = fake_hash_password(password_new)
        db.execute(insert(User).values(username=username_new,
                                       email=email_new,
                                       hashed_password=hashed_password,
                                       disabled=True,
                                       time_create=datetime.now(),
                                       time_update=datetime.now()))
        db.commit()
        messages = f'Успешная регистрация (пользователь: {username_new})'
    context = {
        'request': request,
        'messages': messages,
        'title': 'Регистрация',
        'username_current': username_current,
        'user_id': user_id_current,
    }
    return templates.TemplateResponse("register.html", context)


# Авторизация

@app.get("/login/")
async def login_input(request: Request):
    global user_id_current, username_current
    context = {
        'request': request,
        'title': 'Авторизация',
        'username_current': username_current,
        'user_id': user_id_current,
    }
    return templates.TemplateResponse("login.html", context)


@app.get("/logout/")
async def logout_input(request: Request):
    global user_id_current, username_current
    user_id_current = 0
    username_current = 'гость'
    context = {
        'request': request,
        'title': 'Авторизация',
        'username_current': username_current,
        'user_id': user_id_current,
    }
    return templates.TemplateResponse("login.html", context)


# Меню

@app.get('/menu')
async def menu_str(db: Annotated[Session, Depends(get_db)], request: Request) -> HTMLResponse:
    global user_id_current, username_current, basket_list
    title = 'Меню'
    menus = db.scalars(select(Menu)).all()
    context = {
        'request': request,
        'menus': menus,
        'title': title,
        'username_current': username_current,
        'user_id': user_id_current,
        'basket_list': basket_list,
    }
    return templates.TemplateResponse("menu.html", context)


@app.post('/menu_add')
async def menu_add(db: Annotated[Session, Depends(get_db)], request: Request, key: str = Form()) -> HTMLResponse:
    global user_id_current, username_current, basket_list
    menu_id = int(key)
    if menu_id in basket_list:
        basket_list[menu_id] += 1
    else:
        basket_list.update({menu_id: 1})
    title = 'Меню'
    menus = db.scalars(select(Menu)).all()
    context = {
        'request': request,
        'menus': menus,
        'title': title,
        'username_current': username_current,
        'user_id': user_id_current,
        'basket_list': basket_list,
    }
    return templates.TemplateResponse("menu.html", context)


@app.post('/menu_del')
async def menu_del(db: Annotated[Session, Depends(get_db)], request: Request, key2: str = Form()) -> HTMLResponse:
    global user_id_current, username_current, basket_list
    menu_id = int(key2)
    if menu_id in basket_list:
        if basket_list[menu_id] > 1:
            basket_list[menu_id] -= 1
        elif basket_list[menu_id] == 1:
            basket_list.pop(menu_id)
    title = 'Меню'
    menus = db.scalars(select(Menu)).all()
    context = {
        'request': request,
        'menus': menus,
        'title': title,
        'username_current': username_current,
        'user_id': user_id_current,
        'basket_list': basket_list,
    }
    return templates.TemplateResponse("menu.html", context)


# Корзина

@app.get('/basket')
async def basket(db: Annotated[Session, Depends(get_db)], request: Request) -> HTMLResponse:
    global user_id_current, username_current, basket_list
    list_info = {}
    res = 0
    messages = ''
    for i in basket_list:
        menu = db.scalars(select(Menu).where(Menu.id == i)).first()
        name = menu.name_food
        price = menu.price
        amount = basket_list[i]
        list_info.update({i: f"{name}, количество = {amount}, сумма: {float(price)} руб. * {amount} = {float(price) * amount} руб."})
        res += price * amount
    title = 'Корзина'
    context = {
        'request': request,
        'title': title,
        'list_info': list_info,
        'res': res,
        'messages': messages,
        'username_current': username_current,
        'user_id': user_id_current,
    }
    return templates.TemplateResponse("basket.html", context)


@app.post('/basket_add')
async def basket_add(db: Annotated[Session, Depends(get_db)], request: Request, key: str = Form()) -> HTMLResponse:
    global user_id_current, username_current, basket_list
    list_info = {}
    res = 0
    messages = ''
    menu_id = int(key)
    if menu_id in basket_list:
        basket_list[menu_id] += 1
    else:
        basket_list.update({menu_id: 1})
    for i in basket_list:
        menu = db.scalars(select(Menu).where(Menu.id == i)).first()
        name = menu.name_food
        price = menu.price
        amount = basket_list[i]
        list_info.update({i: f"{name}, количество = {amount}, сумма: {float(price)} руб. * {amount} = {float(price) * amount} руб."})
        res += price * amount
    title = 'Корзина'
    context = {
        'request': request,
        'title': title,
        'list_info': list_info,
        'res': res,
        'messages': messages,
        'username_current': username_current,
        'user_id': user_id_current,
    }
    return templates.TemplateResponse("basket.html", context)


@app.post('/basket_del')
async def basket_del(db: Annotated[Session, Depends(get_db)], request: Request, key2: str = Form()) -> HTMLResponse:
    global user_id_current, username_current, basket_list
    list_info = {}
    res = 0
    messages = ''
    menu_id = int(key2)
    if menu_id in basket_list:
        if basket_list[menu_id] > 1:
            basket_list[menu_id] -= 1
        elif basket_list[menu_id] == 1:
            basket_list.pop(menu_id)
    for i in basket_list:
        menu = db.scalars(select(Menu).where(Menu.id == i)).first()
        name = menu.name_food
        price = menu.price
        amount = basket_list[i]
        list_info.update({
            i: f"{name}, количество = {amount}, сумма: {float(price)} руб. * {amount} = {float(price) * amount} руб."})
        res += price * amount
    title = 'Корзина'
    context = {
        'request': request,
        'title': title,
        'list_info': list_info,
        'res': res,
        'messages': messages,
        'username_current': username_current,
        'user_id': user_id_current,
    }
    return templates.TemplateResponse("basket.html", context)


    #     if 'order' in request.POST:
    #         if request.user.is_authenticated:
    #             user_id = int(request.POST.get('user_id'))
    #             deli = request.POST.get('deli') == 'on'
    #             phone = request.POST.get('phone')
    #             address = request.POST.get('address')
    #             comment = request.POST.get('comment')
    #             delivery = 'self'
    #             if deli:
    #                 res += 200
    #                 delivery = 'avto'
    #             Orders.objects.create(user_id=user_id,
    #                                   summa=res,
    #                                   delivery=delivery,
    #                                   phone=phone,
    #                                   address=address,
    #                                   comment=comment)
    #             number = int(Orders.objects.latest('id').id)
    #             for i in basket_list:
    #                 price = Menu.objects.filter(id=i).values_list('price', flat=True)[0]
    #                 count = int(basket_list[i])
    #                 summa = price * count
    #                 OrderIn.objects.create(order_id=number,
    #                                        menu_id=i,
    #                                        count=count,
    #                                        summa=summa)
    #             basket_list.clear()
    #             list_info.clear()
    #             messages = f'Заказ создан, номер {number}'
    #         else:
    #             messages = 'Для оформления заказа нужно авторизоваться'



app.include_router(user.router)
app.include_router(menu.router)
app.include_router(category.router)

# python -m uvicorn app.main:app

# alembic init app.migrations   # только один раз - это создание папки
# alembic revision --autogenerate -m "Initial migration"    # создана первая миграция но ещё нет в БД
# alembic upgrade head  # загрузили в БД
# alembic revision --autogenerate -m "Initial revision" # последующие миграции
# alembic upgrade head  # загрузили в БД


# <!--<form method="post">-->
# <!--    <div class="dropdown">-->
# <!--        <label for="deli">-->
# <!--            <input type="checkbox" id="deli" name="deli">доставка (200 руб)</label><br><br>-->
#
# <!--        <label for="phone">Введите номер телефона (без 8 и тире):</label><br>-->
# <!--        <input type="text" id="phone" name="phone" maxlength="10" size="10" required><br><br>-->
#
# <!--        <label for="address">Введите адрес:</label><br>-->
# <!--        <input type="text" id="address" name="address" maxlength="200" size="160" required><br><br>-->
#
# <!--        <label for="comment">Комментарий к заказу:</label><br>-->
# <!--        <input type="text" id="comment" name="comment" maxlength="500" size="160"><br><br>-->
#
# <!--        <input type="hidden" id="user_id" name="user_id" maxlength="30" value="{{ user.id }}" required>-->
# <!--        <button type="submit" name="order">Заказать</button>-->
# <!--    </div>-->
# <!--</form>-->




