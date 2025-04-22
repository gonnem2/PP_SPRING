from datetime import datetime
from typing import Literal
from pydantic import BaseModel


class SellReceiptResponse(BaseModel):
    receipt_id: int
    status: Literal["paid"]
    sold_at: datetime
