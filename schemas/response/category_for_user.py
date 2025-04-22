from pydantic import BaseModel


class CategoryResponse(BaseModel):
    parent_id: int | None
    id: int
    title: str

    class Config:
        from_attributes = True  # Аналог orm_mode в Pydantic v2
