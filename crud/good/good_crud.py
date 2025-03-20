from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from models import Category
from models.article import Article
from schemas.requests.good_from_user import GoodFromUser


async def get_goods_by_name(db: AsyncSession, name: str):
    data = await db.scalar(select(Article).where(Article.name == name))
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


async def get_all_goods(db: AsyncSession):
    """
    Возвращает список из всех goods в БД
    """

    data = await db.scalars(select(Article))
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


async def get_products_by_category(category_id: int, db: AsyncSession):
    if not (
        get_category := await db.scalar(
            select(Category).where(Category.id == category_id)
        )
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Такой категории не существует",
        )

    products_from_db = await db.scalars(
        select(Article).where(Article.category_id == category_id)
    )
    return products_from_db.all()


async def update_stock_quantity(good_id: int, quantity_change: int, db: AsyncSession):
    good = await db.scalar(select(Article).where(Article.id == good_id))
    if not good:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Товар не найден",
        )
    good.stock_quantity += quantity_change
    await db.commit()
