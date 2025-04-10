from datetime import datetime

from pydantic import BaseModel


class ReceiptResponse(BaseModel):
    id: int
    user_id: int
    created_at: datetime
    status: str

    class Config:
        from_attributes = True
