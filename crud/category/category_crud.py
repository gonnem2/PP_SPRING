from fastapi import HTTPException, status
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from models import Category
from schemas.requests.CategoryRequest import CategoryRequest
from schemas.requests.pagination import PaginationParams


async def category_in_db(db: AsyncSession, category_name: str):
    from_db = await db.scalar(select(Category).where(Category.title == category_name))
    return bool(from_db)


async def create_category(
    db: AsyncSession, category_from_user: CategoryRequest, current_user: dict
):
    """Создает категорию"""

    if not current_user.get("is_owner"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="У вас нет прав на добавление категории",
        )

    if await category_in_db(db, category_from_user.name):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Категория с таким именем уже создана",
        )
    new_category = Category(
        title=category_from_user.name, parent_id=category_from_user.parent_id
    )
    db.add(new_category)
    await db.commit()
    return True


async def get_categories(db: AsyncSession, pagination: PaginationParams):
    """Возвращает список категорий с нужным оффсетом"""

    categories_from_db = await db.scalars(
        select(Category).offset(pagination.offset).limit(pagination.size)
    )

    if not (result := categories_from_db.all()):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Категорий в БД не найдено!"
        )

    return result


async def get_category_by_id(category_id: int, db: AsyncSession):
    """Возвращает категорию по id"""

    if not (
        category := await db.scalar(select(Category).where(Category.id == category_id))
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Категории с таким id не существует!",
        )

    return category


async def put_category_by_id(
    db: AsyncSession,
    category_id: int,
    category: CategoryRequest,
):
    if not get_category_by_id(category_id, db):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Категории с таким id не существует!",
        )

    await db.execute(
        update(Category)
        .where(Category.id == category_id)
        .values(parent_id=category.parent_id, title=category.name)
    )
    await db.commit()
    return True


async def delete_category(
    db: AsyncSession,
    category_id: int,
    current_user: dict,
):
    if not (current_user.get("is_owner")):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="У вас нет доступа к этой операции!",
        )

    if not await get_category_by_id(category_id, db):
        return True

    await db.execute(delete(Category).where(Category.id == category_id))
    await db.commit()
    return True


async def sell_receipt(receipt_id: int, current_user: dict, db: AsyncSession): ...
