from pydantic import BaseModel


class GoodFromUser(BaseModel):
    name: str
    category_id: int
    price: int
    cost_price: int
    stock_quantity: int
