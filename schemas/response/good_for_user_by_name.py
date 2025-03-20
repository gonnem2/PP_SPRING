from pydantic import BaseModel


class GoodAnswer(BaseModel):
    name: str
    description: str
