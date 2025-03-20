from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession

from models import Category, Sales
from models.article import Article
from schemas.requests.good_from_user import GoodFromUser
from schemas.response.GoodStatistic import GoodStat


async def get_goods_by_name(db: AsyncSession, name: str):
    data = await db.scalar(select(Article).where(Article.name.ilike(f"%{name}%")))
    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Товар с таким именем не найден",
        )
    return data


async def get_good_by_id(good_id: int, db: AsyncSession):
    good_from_db = await db.scalar(select(Article).where(Article.id == good_id))
    if not good_from_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Товар в БД не найден",
        )
    return good_from_db


async def add_good(good: GoodFromUser, db: AsyncSession):
    """
    Добавляет товар в Бд, если его там - нет
    """

    if await db.scalar(select(Article).where(Article.name == good.name)):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Товар с таким названием уже в существует",
        )
    category_from_db = await db.scalar(
        select(Category).where(Category.id == good.category_id)
    )
    if not category_from_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Категории с таким id не существует",
        )

    good_for_db = Article(
        name=good.name,
        category_id=good.category_id,
        price=good.price,
        cost_price=good.cost_price,
        stock_quantity=good.stock_quantity,
        created_at=datetime.now(),
    )

    db.add(good_for_db)
    await db.commit()

    return {
        "name": good.name,
        "message": "Created",
    }


async def get_all_goods(db: AsyncSession, skip, limit):
    """
    Возвращает список из всех goods в БД
    """

    data = await db.scalars(select(Article).offset(skip).limit(limit))
    if not (goods_from_db := data.all()):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="База данных пуста"
        )
    return goods_from_db


async def update_good(good_id: int, good: GoodFromUser, db: AsyncSession):

    if not get_goods_by_name(db, good.name):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Товара с таким названием в БД - НЕТ",
        )

    category_from_db = await db.scalar(
        select(Category).where(Category.id == good.category_id)
    )
    if not category_from_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Категории с таким id не существует",
        )

    await db.execute(
        update(Article)
        .where(Article.id == good_id)
        .values(
            name=good.name,
            category_id=good.category_id,
            price=good.price,
            cost_price=good.cost_price,
            stock_quantity=good.stock_quantity,
        )
    )
    await db.commit()
    return good.name


async def delete_product_by_id(product_id: int, db: AsyncSession):
    if not (good := await get_good_by_id(product_id, db)):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Товар в БД не найден",
        )

    await db.delete(good)
    await db.commit()
    return {
        "message": "Товар успешно удален",
    }


async def get_products_by_category(
    category_id: int,
    db: AsyncSession,
    min_price,
    max_price,
    min_stock_quantity,
    max_stock_quantity,
):
    if not (
        get_category := await db.scalar(
            select(Category).where(Category.id == category_id)
        )
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Такой категории не существует",
        )

    query = select(Article).where(Article.category_id == category_id)

    if min_price is not None:
        query = query.where(Article.price >= min_price)
    if max_price is not None:
        query = query.where(Article.price <= max_price)
    if min_stock_quantity is not None:
        query = query.where(Article.stock_quantity >= min_stock_quantity)
    if max_stock_quantity is not None:
        query = query.where(Article.stock_quantity <= max_stock_quantity)

    products_from_db = await db.scalars(query)

    if not (products_from_db := products_from_db.all()):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Такие товары не найдены",
        )

    return products_from_db


async def update_stock_quantity(good_id: int, quantity_change: int, db: AsyncSession):
    good = await db.scalar(select(Article).where(Article.id == good_id))
    if not good:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Товар не найден",
        )
    good.stock_quantity += quantity_change
    await db.commit()


async def get_prod_stat(db: AsyncSession, product_id: int, start_date, end_date):
    """Возвращает словарь со статистикой"""

    product = await get_good_by_id(product_id, db)

    if start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Дата начала должна быть меньше или равна дате окончания",
        )

    product_sales_count = await db.scalar(
        select(func.count())
        .where(Sales.good_id == product_id)
        .where(Sales.sales_date >= start_date)
        .where(Sales.sales_date <= end_date)
    )

    # Общая выручка
    product_revenue = await db.scalar(
        select(func.sum(Sales.total_price))
        .where(Sales.good_id == product_id)
        .where(Sales.sales_date >= start_date)
        .where(Sales.sales_date <= end_date)
    )

    # Выручка без наценки
    total_cost = await db.scalar(
        select(func.sum(Sales.quantity * Article.cost_price))
        .where(Sales.good_id == product_id)
        .where(Sales.sales_date >= start_date)
        .where(Sales.sales_date <= end_date)
    )
    profit = product_revenue - total_cost if product_revenue else 0

    return GoodStat(
        product_id=product_id,
        product_name=product.name,
        product_sales_count=product_sales_count or 0,
        product_revenue=product_revenue or 0,
        profit=profit or 0,
        product_quantity=product.stock_quantity,
    )
