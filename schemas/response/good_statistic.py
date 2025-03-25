from pydantic import BaseModel


class GoodStat(BaseModel):
    product_id: int
    product_name: str
    product_sales_count: int
    product_revenue: int
    profit: int
    product_quantity: int
