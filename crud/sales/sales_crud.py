from fastapi import HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession

from models import ReceiptItem
from models.sales import Sales


async def add_items_to_sales_table(
    items_from_receipt: list[ReceiptItem],
    db: AsyncSession,
    user_id: int,
    receipt_id: int,
):
    if not items_from_receipt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Корзина пуста"
        )

    # создание новых объектов sales
    sales_objects = []
    for item in items_from_receipt:
        total_price = item.price_at_sale * item.quantity
        new_sales_obj = Sales(
            good_id=item.product_id,
            quantity=item.quantity,
            user_id=user_id,
            total_price=total_price,
            receipt_id=receipt_id,
        )
        sales_objects.append(new_sales_obj)

    db.add_all(sales_objects)

    # Коммит


async def set_closed_status_for_receipt(db, receipt_from_db):
    receipt_from_db.status = "closed"
