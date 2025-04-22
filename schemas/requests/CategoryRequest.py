from pydantic import BaseModel, Field


class CategoryRequest(BaseModel):

    name: str
    parent_id: int | None = Field(default=None, examples=[None])
