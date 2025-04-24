from datetime import datetime

from fastapi import HTTPException, status

from sqlalchemy import select

from sqlalchemy.ext.asyncio import AsyncSession

from crud.cash.cash_crud import (
    get_items_from_receipt,
    del_items_from_receipt_items_table,
)
from crud.sales.sales_crud import (
    add_items_to_sales_table,
    set_closed_status_for_receipt,
)
from models import Receipt
from schemas.response.sell_receipt import SellReceiptResponse


async def sell_receipt(receipt_id: int, current_user: dict, db: AsyncSession):
    receipt_from_db = await db.scalar(select(Receipt).where(Receipt.id == receipt_id))

    if not receipt_from_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Чека с таким id - нет"
        )

    if receipt_from_db.status == "closed":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Чек уже закрыт"
        )

    if receipt_from_db.user_id != current_user.get("id", 0):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="У вас нед доступа к этому чеку",
        )

    # Получение списка товаров из таблицы с товарами из чека
    items_from_receipt = await get_items_from_receipt(receipt_id, db)

    # Добавление товаров в таблицу sales
    await add_items_to_sales_table(
        items_from_receipt, db, current_user.get("id"), receipt_id
    )

    # удаление данных из таблицы ReceiptItems, доступ к ним будет осуществляться через Sales
    await del_items_from_receipt_items_table(receipt_id, db)

    # изменение статуса чека с open на closed
    await set_closed_status_for_receipt(db, receipt_from_db)

    try:
        await db.commit()
    except Exception:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Ошибка при сохранении данных",
        )

    return SellReceiptResponse(
        receipt_id=receipt_id, status="paid", sold_at=datetime.now()
    )
