### (Реализация на FastAPI по дипломной работе ниже)

# Дипломная работа по теме: 
## «Разработка простого веб-приложения с использованием фреймворков: Django, Flask и FastAPI, сравнение преимуществ и недостатков между ними».

# Описание проекта

  ### Сайт доставки еды

  Данный сайт предназначен принимать заказы.
  
## Возможные действия пользователя:
  
####	• Регистрация
####	• Авторизация
####	• Выход из личного кабинета
####	• Возможность выбрать товары и способ доставки
####	• Возможность оформить заказ
####	• И доступ к просмотру истории и содержанию заказов

  
# Страницы сайта:

### 1. Главная страница (для всех пользователей)

![1](https://raw.githubusercontent.com/Vorobish/Diploma-work/refs/heads/main/image/image.png) 

### 2. Меню (для всех пользователей)

![2](https://raw.githubusercontent.com/Vorobish/Diploma-work/refs/heads/main/image/image-1.png)

### 3. Корзина (для всех пользователей)

![3](https://raw.githubusercontent.com/Vorobish/Diploma-work/refs/heads/main/image/image-2.png)

### 4. Заказы (для авторизованных пользователей)

![4](https://raw.githubusercontent.com/Vorobish/Diploma-work/refs/heads/main/image/image-3.png)

### 5. Заказ (для авторизованных пользователей, отсутствует в основном меню, открывается только по переходу из страницы «Заказы»)

![5](https://raw.githubusercontent.com/Vorobish/Diploma-work/refs/heads/main/image/image-4.png)

### 6. Авторизация, кнопка «Войти» (для неавторизованных пользователей)

![6](https://raw.githubusercontent.com/Vorobish/Diploma-work/refs/heads/main/image/image-5.png)

### 7. Регистрация, кнопка «Зарегистрироваться» (для неавторизованных пользователей)

![7](https://raw.githubusercontent.com/Vorobish/Diploma-work/refs/heads/main/image/image-6.png)

### 8. Кнопка «Выйти» - не страница, видна только для авторизованных пользователей

![8](https://raw.githubusercontent.com/Vorobish/Diploma-work/refs/heads/main/image/image-7.png)

# Как запустить
  
####  1. Склонируйтке проект и перейдите в директорию проекта.
####  2. Установите необходимые библиотеки выполнив следующую команду: pip install -r requirements.txt.
####  3. Запустите код с помощью соответствующей команды для каждого фреймворка:
     3.1. Для Django, в терминале:
         • Заходим в виртуальное окружение: .venv/Scripts/activate
         • Переходим в папку проекта: cd FoodProject
         • Команда запуска: python manage.py runserver 8000
         • Сайт запущен, можно перейти по ссылке (http://127.0.0.1:8000/)
         • Для выхода: Ctrl + C

     3.2. Для FastAPI, в терминале: 
         • Команда: python -m uvicorn app.main:app
         • Сайт запущен, можно перейти по ссылке (http://127.0.0.1:8000/) добавив "base" - главная страница
         • Для выхода: Ctrl + C

     3.3. Для Flask, в терминале:
         • Заходим в виртуальное окружение: .venv/Scripts/activate
         • В дереве открываем модуль views (в пакете app) и запускаем (Run >)
         • Сайт запущен, можно перейти по ссылке (http://127.0.0.1:5000/)
         • Для выхода: Нажимаем Stop

# Основные библиотеки помимо самих django, fastapi, flask

1. SQLAlchemy — это библиотека для Python, которая позволяет работать с реляционными базами данных с помощью ORM (объектно-реляционного отображения)
2. alembic - это инструмент для миграции базы данных, используемый в SQLAlchemy
3. Jinja2 (Jinja) — это язык шаблонов, использующийся в Python.
4. Pydantic — это библиотека, которая предлагает простой способ валидации и сериализации данных
5. Uvicorn — это ASGI-сервер, который позволяет запускать асинхронные приложения на Python, такие как FastAPI
