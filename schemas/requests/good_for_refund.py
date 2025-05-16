from pydantic import BaseModel


class GoodForRefund(BaseModel):
    good_id: int
    quantity: int
