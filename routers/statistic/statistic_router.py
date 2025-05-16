from datetime import datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db import get_db
from routers.auth.utils import get_current_user
from schemas.response.statistic_sales_response import SalesStatsResponse
from services.statisitc.statistic import get_sales_stat

router = APIRouter(
    prefix="/statistic",
    tags=["Статистика"],
)


@router.get(
    "/",
    summary="Возвращает статистику по проданным товарам за указанную дату",
)
async def get_sales_stat_endpoint(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
    start_date: Annotated[datetime, Query(...)] = datetime.now() - timedelta(days=1),
    end_date: Annotated[datetime, Query()] = datetime.now().date(),
) -> SalesStatsResponse:
    stat = await get_sales_stat(db, current_user, start_date, end_date)
    return stat
