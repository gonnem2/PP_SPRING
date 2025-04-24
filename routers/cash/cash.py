from typing import Annotated

from fastapi import APIRouter, Depends, Body, status, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db import get_db
from crud.cash.cash_crud import (
    create_receipt,
    add_items_to_receipt,
    get_all_receipts,
    delete_product_from_receipt,
    get_check_info,
)
from routers.auth.utils import get_current_user
from schemas.requests.pagination import PaginationParams
from schemas.response.receipt_responce import ReceiptResponse
from schemas.response.sell_receipt import SellReceiptResponse

router = APIRouter(prefix="/cash", tags=["Логика Кассы"])


@router.post("/receipts", summary="Создает новый чек", response_model=ReceiptResponse)
async def create_new_receipt(
    current_user: Annotated[dict, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    res = await create_receipt(current_user, db)
    return res


@router.get("/receipts", summary="Возвращает все чеки")
async def get_all_receipts_endpoint(
    current_user: Annotated[dict, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    pagination: Annotated[PaginationParams, Query()],
):
    result = await get_all_receipts(current_user, db, pagination)
    return result


@router.post(
    "/receipts/{receipt_id}/add",
    summary="Добавить товары в чек",
    description="Добавляет товары в таблицу, в которой есть cсылка на чек (его id)",
    status_code=status.HTTP_200_OK,
)
async def add_items_to_receipt_endpoint(
    current_user: Annotated[dict, Depends(get_current_user)],
    good_id: int,
    count: int,
    purchase_id: Annotated[int, Body(gt=0)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    if good := await add_items_to_receipt(
        current_user, good_id, count, purchase_id, db
    ):
        return {"detail": f"{good} в количестве {count}, добавлен в чек"}


@router.delete(
    "/receipts/{receipt_id}/delete/{product_id}",
    summary="Удаляет товар из корзины",
    status_code=status.HTTP_200_OK,
)
async def delete_product_from_receipt_endpoint(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
    receipt_id: Annotated[int, Path(gt=0)],
    product_id: Annotated[int, Path(gt=0)],
):
    res = await delete_product_from_receipt(db, current_user, receipt_id, product_id)
    return {"detail": "Товар удален"}


@router.get("/receipts/{receipt_id}", summary="Возвращает товары из чека")
async def show_check_info(
    current_user: Annotated[dict, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    receipt_id: Annotated[int, Path(gt=0)],
):
    res = await get_check_info(current_user, db, receipt_id)
    return res


@router.post(
    "/receipts/{receipt_id}/sell",
    summary="Завершить продажу по чеку",
    response_model=SellReceiptResponse,
    status_code=status.HTTP_200_OK,
)
async def sell_receipt_endpoint(
    receipt_id: Annotated[int, Path(gt=0)],
    current_user: Annotated[dict, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    await sell_receipt(receipt_id, current_user, db)



