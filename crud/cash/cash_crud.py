from fastapi import status, HTTPException
from sqlalchemy import select, update, delete

from sqlalchemy.ext.asyncio import AsyncSession

from models import Article, ReceiptItem, Sales
from models.receipt import Receipt
from schemas.requests.pagination import PaginationParams


async def check_permission_owner_or_seller(current_user: dict):
    if not (current_user.get("is_seller") or current_user.get("is_owner")):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="У вас нет доступа к этой операции",
        )


async def create_receipt(current_user: dict, db: AsyncSession):
    await check_permission_owner_or_seller(current_user)
    new_receipt = Receipt(user_id=current_user["id"])
    db.add(new_receipt)
    await db.commit()
    await db.refresh(new_receipt)
    return new_receipt


async def add_items_to_receipt(
    current_user: dict,
    good_id: int,
    count: int,
    receipt_id: int,
    db: AsyncSession,
):

    await check_permission_owner_or_seller(current_user)

    await check_receipt_status(db, receipt_id)

    good_from_db = await db.scalar(select(Article).where(Article.id == good_id))

    if not good_from_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Товара с таким id в БД не найдено",
        )

    if good_from_db.stock_quantity < count:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Товара в таком количестве нет, доступно: {good_from_db.stock_quantity}",
        )

    await db.execute(
        update(Article)
        .where(Article.id == good_id)
        .values(stock_quantity=Article.stock_quantity - count)
    )

    item_from_db = await db.scalar(
        select(ReceiptItem).where(ReceiptItem.product_id == good_id)
    )
    if item_from_db:
        await db.execute(
            update(ReceiptItem)
            .where(ReceiptItem.product_id == good_id)
            .values(quantity=ReceiptItem.quantity + count)
        )
    else:
        items = ReceiptItem(
            receipt_id=receipt_id,
            product_id=good_id,
            quantity=count,
            price_at_sale=good_from_db.price,
        )
        db.add(items)
    receipt_from_db: Receipt = await db.scalar(
        select(Receipt).where(Receipt.id == receipt_id)
    )
    receipt_from_db.total_amount = (
        float(receipt_from_db.total_amount) + float(good_from_db.price) * count
    )

    await db.commit()
    await db.refresh(good_from_db)

    return good_from_db.name


async def get_all_receipts(
    current_user: dict, db: AsyncSession, pagination: PaginationParams
):

    await check_permission_owner_or_seller(current_user)

    if not (
        receipts_from_db := await db.scalar(
            select(Receipt).offset(pagination.offset).limit(pagination.size)
        )
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Чеков не создано"
        )
    return receipts_from_db


async def check_receipt_status(db, receipt_id):
    receipt_from_db = await db.scalar(select(Receipt).where(Receipt.id == receipt_id))

    if receipt_from_db.status == "closed":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Чек закрыт")


async def check_receipt_in_db(db, receipt_id, current_user):
    receipt_from_db = await db.scalar(select(Receipt).where(Receipt.id == receipt_id))
    if not receipt_from_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Чека с таким id - нет"
        )

    if current_user.get("id") != receipt_from_db.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Это не ваш чек",
        )
    return receipt_from_db


async def delete_product_from_receipt(
    db: AsyncSession, current_user: dict, receipt_id: int, product_id: int, count: int
):
    await check_receipt_status(db, receipt_id)
    receipt_from_db: Receipt = await check_receipt_in_db(db, receipt_id, current_user)

    product_from_db: ReceiptItem = await db.scalar(
        select(ReceiptItem).where(ReceiptItem.product_id == product_id)
    )
    if not product_from_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Такого тоавра нет"
        )

    if count > product_from_db.quantity:
        raise HTTPException(status_code=400, detail="Слишком много товаров!")

    product_from_db.quantity -= count

    if product_from_db.quantity <= 0:
        await db.execute(
            delete(ReceiptItem).where(ReceiptItem.product_id == product_id)
        )

    receipt_from_db.total_amount = (
        float(receipt_from_db.total_amount) - product_from_db.price_at_sale * count
    )

    # вовзрат в товаров в БД
    await db.execute(
        update(Article)
        .where(Article.id == product_id)
        .values(stock_quantity=Article.stock_quantity + product_from_db.quantity)
    )
    await db.commit()
    return True


async def get_check_info(current_user: dict, db: AsyncSession, receipt_id: int):
    receipt_from_db = await check_receipt_in_db(db, receipt_id, current_user)
    items = await db.scalars(
        select(ReceiptItem).where(ReceiptItem.receipt_id == receipt_from_db.id)
    )
    items = items.all()
    return items


async def get_items_from_receipt(receipt_id: int, db: AsyncSession):
    items = await db.scalars(
        select(ReceiptItem).where(ReceiptItem.receipt_id == receipt_id)
    )
    return items.all()


async def del_items_from_receipt_items_table(receipt_id: int, db: AsyncSession):
    await db.execute(delete(ReceiptItem).where(ReceiptItem.receipt_id == receipt_id))


async def receipt_from_sales_table(db: AsyncSession, receipt_id):
    if receipt := await db.scalar(select(Sales).where(Sales.receipt_id == receipt_id)):
        return receipt
    raise HTTPException(status=status.HTTP_404_NOT_FOUND, detail="Такого чека нет!")


async def del_items_from_sales_table(
    product_id: int, quantity: int, db: AsyncSession, receipt_id: int
):
    sale_prod: Sales = await db.scalar(
        select(Sales).where(
            Sales.receipt_id == receipt_id and Sales.good_id == product_id
        )
    )

    sale_prod.quantity -= quantity
    if sale_prod.quantity == 0:
        await db.delete(sale_prod)

    await db.commit()


async def get_all_sold_receipts(
    db: AsyncSession, current_user: dict, pagination: PaginationParams
):
    query = (
        select(Receipt)
        .where(Receipt.status == "closed")
        .order_by(Receipt.created_at.desc())  # Сортировка по дате
        .limit(pagination.size)
        .offset(pagination.offset)
    )
    result = await db.scalars(query)
    receipts = result.all()

    return receipts


async def get_user_receipts_from_db(
    db: AsyncSession, current_user: dict, pagination: PaginationParams
):
    results = await db.scalars(
        select(Receipt)
        .limit(pagination.size)
        .offset(pagination.offset)
        .where(Receipt.user_id == current_user.get("id"))
    )
    return results.all()
