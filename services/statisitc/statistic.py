from collections import defaultdict
from datetime import datetime, date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from crud.statistic.statistic_crud import get_sales_stats


async def get_sales_stat(
    db: AsyncSession, current_user: dict, start_date: datetime, end_date: date
):
    # Проданные товары за период
    if not current_user.get("is_owner"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="У вас нет прав на эту операцию!",
        )

    sales_product = await get_sales_stats(db, start_date, end_date)

    if not sales_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="За указанный период -  нет продаж!",
        )

    return sales_product
