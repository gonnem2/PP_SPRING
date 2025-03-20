from pydantic import BaseModel


class GoodAnswerId(BaseModel):
    id: int
    description: str
