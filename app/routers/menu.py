from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.backend.dp_depends import get_db
from app.models import Menu

# from slugify import slugify
from sqlalchemy import select, insert, update, delete


router = APIRouter(prefix="/menu", tags=["menu"])


@router.get("/")
async def all_menu(db: Annotated[Session, Depends(get_db)]):
    menus = db.scalars(select(Menu)).all()
    return menus


# 2024-11-08 20:34:41	1	Пицца	FoodProject\static\vegan1.jpg	2024-11-08 20:34:49.570500
# 2024-11-08 20:36:35	2	Напитки	FoodProject\static\mors1.webp	2024-11-08 20:36:36.951563
#
# 2024-11-08 20:38:01	1	Зелёная пицца	700	800	мука, вода, соль, шпинат, хумус, руккола, лук, чеснок, томатный соус, оливковое масло, дрожжи, перец	vegan1.jpg	2024-11-08 20:43:24.989885	1
# 2024-11-08 20:43:29	2	Пицца с перчиком	700	900	мука, вода, соль, болгарский перец, грибы, помидоры, лук, чеснок, томатный соус, оливковое масло, дрожжи, перец	vegan2.jpg	2024-11-08 20:45:02.998586	1
# 2024-11-08 20:45:05	3	Овощная пицца с сыром	800	1000	мука, вода, соль, брокколи, кабачок, маслины, помидоры, веганский сыр, лук, чеснок, томатный соус, оливковое масло, перец	pizza3.webp	2024-11-08 20:47:23.789461	1
# 2024-11-08 20:47:26	4	Пицца "Овощное изобилие"	800	1100	мука, вода, соль, шпинат, помидоры, маслины гигант, баклажаны, лук, чеснок, томатный соус, оливковое масло, базилик, перец	pizza4.jpeg	2024-11-08 20:49:29.613406	1
# 2024-11-08 20:49:32	5	Морс брусничный	1000	150	Вода, брусника, сахар	mors1.webp	2024-11-08 20:50:50.056130	2
# 2024-11-08 20:50:59	6	Морс облепиховый	1000	150	Вода, облепиха, сахар	mors2.webp	2024-11-08 20:52:10.382058	2
