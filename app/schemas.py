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



