from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from watchfiles import awatch

from backend.db import get_db
from crud.cash.cash_crud import create_receipt
from routers.auth.utils import get_current_user
from schemas.response.receipt_responce import ReceiptResponse

router = APIRouter(prefix="/cash", tags=["Логика Кассы"])


@router.post("/receipts", summary="Создает новый чек", response_model=ReceiptResponse)
async def create_new_receipt(
    current_user: Annotated[dict, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    res = await create_receipt(current_user, db)
    return res
