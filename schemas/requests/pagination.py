from pydantic import BaseModel
from fastapi import Query


class PaginationParams(BaseModel):
    page: int = Query(default=1, ge=1, description="Номер страницы (начиная с 1)")
    size: int = Query(
        default=10, ge=1, le=100, description="Количество элементов на странице"
    )

    @property
    def offset(self) -> int:
        """Вычисляет смещение для SQL-запросов (например, LIMIT + OFFSET)."""
        return (self.page - 1) * self.size
