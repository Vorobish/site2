from typing import Union

from pydantic import BaseModel


class CreateMenu(BaseModel):
    name_food: str
    category_id: str
    weight_gr: int
    price: float
    ingredients: str
    image: str


class CreateCategory(BaseModel):
    name_category: str


class UserAuth(BaseModel):
    username: str
    email: Union[str, None] = None
    full_name: Union[str, None] = None
    disabled: Union[bool, None] = None


class CreateUser(BaseModel):
    username: str
    email: str
    password: str
    disabled: int


# class CreateUserInDB(CreateUser):
#     hashed_password: str

# class UpdateUser(BaseModel):
#     firstname: str
#     lastname: str
#     age: int
