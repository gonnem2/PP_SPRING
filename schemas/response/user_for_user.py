from pydantic import BaseModel


class UserGet(BaseModel):
    name: str
    message: str

    class Config:
        from_attributes = True
