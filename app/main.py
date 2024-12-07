from datetime import datetime

from fastapi import FastAPI, Request, Depends, HTTPException, status, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from typing import Annotated, Union
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import select, insert, update, delete
from sqlalchemy.orm import Session

from app.backend.dp_depends import get_db
from app.models import Menu, Order, OrderIn
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
basket_list = {}

'''
    Блок Авторизация (Auth2)
'''


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
            'username_current': username_current,
            'user_id': user_id_current,
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
            'username_current': username_current,
            'user_id': user_id_current,
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


'''
    Блок Главная страница
'''


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


'''
    Блок Регистрация
'''


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


'''
    Блок Авторизация (страница)
'''


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


'''
    Блок Меню
'''


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


'''
    Блок Корзина
'''


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
        list_info.update(
            {i: f"{name}, количество = {amount}, сумма: {float(price)} руб. * {amount} = {float(price) * amount} руб."})
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
        list_info.update(
            {i: f"{name}, количество = {amount}, сумма: {float(price)} руб. * {amount} = {float(price) * amount} руб."})
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


@app.post('/basket_order')
async def basket_order(db: Annotated[Session, Depends(get_db)], request: Request
                       , deli: str = Form(), phone: str = Form(), address: str = Form()
                       , comment: str = Form()) -> HTMLResponse:
    global user_id_current, username_current, basket_list
    list_info = {}
    res = 0
    messages = ''
    for i in basket_list:
        menu = db.scalars(select(Menu).where(Menu.id == i)).first()
        name = menu.name_food
        price = menu.price
        amount = basket_list[i]
        list_info.update({
            i: f"{name}, количество = {amount}, сумма: {float(price)} руб. * {amount} = {float(price) * amount} руб."})
        res += price * amount
    if user_id_current:
        delivery = 'self'
        if deli == 'avto':
            res += 200
            delivery = 'avto'
        db.execute(insert(Order).values(user_id=user_id_current,
                                        summa=res,
                                        delivery=delivery,
                                        phone=phone,
                                        address=address,
                                        comment=comment))
        number = db.scalars(select(Order).order_by(Order.id.desc())).first()
        for i in basket_list:
            menu = db.scalars(select(Menu).where(Menu.id == i)).first()
            price = menu.price
            count = basket_list[i]
            summa = price * count
            db.execute(insert(OrderIn).values(order_id=number.id,
                                              menu_id=i,
                                              count=count,
                                              summa=summa))
        basket_list.clear()
        list_info.clear()
        messages = f'Заказ создан, номер {number.id}'
    else:
        messages = 'Для оформления заказа нужно авторизоваться'
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
    db.commit()
    return templates.TemplateResponse("basket.html", context)


'''
    Блок Заказы
'''


@app.get('/orders')
async def orders(db: Annotated[Session, Depends(get_db)], request: Request) -> HTMLResponse:
    global user_id_current, username_current
    orderss = db.scalars(select(Order).where(Order.user_id == user_id_current).order_by(Order.id.desc()))
    title = 'Заказы'
    context = {
        'request': request,
        'title': title,
        'username_current': username_current,
        'user_id': user_id_current,
        'orderss': orderss,
    }
    return templates.TemplateResponse("orders.html", context)


@app.get('/order/{order_id}/')
async def order(db: Annotated[Session, Depends(get_db)], request: Request, order_id: int = int()) -> HTMLResponse:
    global user_id_current, username_current
    order = db.scalars(select(Order).where(Order.id == order_id)).first()
    if user_id_current == order.user_id:
        summa = order.summa
        delivery = order.delivery
        deli_info = ''
        if delivery == 'avto':
            deli_info = 'с доставкой (200 руб.)'
        else:
            deli_info = 'самовывоз'
        pay_stat = order.pay_stat
        pay_info = ''
        if pay_stat == 'paid':
            pay_info = 'заказ оплачен'
        elif pay_stat == 'part':
            pay_info = 'внесен аванс'
        else:
            pay_info = 'не оплачен'
        status = order.status
        stat_info = ''
        if status == 1:
            stat_info = 'создан'
        elif status == 2:
            stat_info = 'принят'
        elif status == 3:
            stat_info = 'отказан'
        elif status == 4:
            stat_info = 'в работе'
        elif status == 5:
            stat_info = 'готов'
        elif status == 6:
            stat_info = 'у курьера'
        else:
            stat_info = 'исполнен'
        detail = db.scalars(select(OrderIn).where(OrderIn.id == order_id))
        list_detail = []
        for i in detail:
            menu = db.scalars(select(Menu).where(Menu.id == i.menu_id)).first()
            count = i.count
            name = menu.name_food
            price = menu.price
            list_detail.append(
                f"{name}, количество = {count}, сумма: {float(price)} руб. * {count} = {float(price) * count} руб.")
        title = 'Детали заказа'
        context = {
            'request': request,
            'username_current': username_current,
            'user_id': user_id_current,
            'title': title,
            'order_id': order_id,
            'summa': summa,
            'deli_info': deli_info,
            'phone': order.phone,
            'address': order.address,
            'pay_info': pay_info,
            'stat_info': stat_info,
            'comment': order.comment,
            'time_create': order.time_create,
            'list_detail': list_detail,
        }
        return templates.TemplateResponse("order.html", context)
    else:
        return HTMLResponse('Для просмотра заказа нужно авторизоваться!', status_code=400)


app.include_router(user.router)
app.include_router(menu.router)
app.include_router(category.router)

# python -m uvicorn app.main:app

# alembic revision --autogenerate -m "Initial revision" # последующие миграции
# alembic upgrade head  # загрузили в БД
