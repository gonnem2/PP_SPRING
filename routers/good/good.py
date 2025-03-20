from typing import Annotated

from fastapi import APIRouter, status, HTTPException, Path

from fastapi.params import Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db import get_db
from crud.good.good_crud import (
    add_good,
    get_all_goods,
    get_goods_by_name,
    update_good,
    delete_product_by_id,
    get_good_by_id,
    get_products_by_category,
    update_stock_quantity,
)
from schemas.requests.good_from_user import GoodFromUser
from schemas.response.good_for_user_by_id import GoodAnswerId
from schemas.response.good_for_user_by_name import GoodAnswer

router = APIRouter(prefix="/good", tags=["Товар"])


@router.get(
    "/by_category",
    summary="Возвращает товары по айди категории",
    status_code=status.HTTP_200_OK,
)
async def get_goods_by_category(
    db: Annotated[AsyncSession, Depends(get_db)],
    category_id: Annotated[int, Query(...)],
):
    products_from_db = await get_products_by_category(category_id, db)

    return products_from_db


@router.get("/by_id/{product_id}", summary="Возвращает товар по id")
async def get_prod_by_id(
    product_id: Annotated[int, Path(...)], db: Annotated[AsyncSession, Depends(get_db)]
):
    response = await get_good_by_id(product_id, db)
    return GoodAnswerId(
        id=response,
        description="Товар успешно найден",
    )


@router.get(
    "/all_product",
    summary="Возвращает все товары из БД",
    status_code=status.HTTP_200_OK,
)
async def get_goods(db: Annotated[AsyncSession, Depends(get_db)]):
    data = await get_all_goods(db)
    return data


@router.get(
    "/by_name",
    summary="Возвращает информацию о товаре по имени",
    status_code=status.HTTP_200_OK,
)
async def get_good_by_name(
    name: Annotated[str, Query(...)], db: Annotated[AsyncSession, Depends(get_db)]
):
    data = await get_goods_by_name(db, name)
    return data


@router.post("/", summary="Добавить товар", status_code=status.HTTP_201_CREATED)
async def add_new_good(
    good: GoodFromUser, db: Annotated[AsyncSession, Depends(get_db)]
):
    data = await add_good(good, db)
    return data


@router.put(
    "/{good_id}", summary="Обновляет продукт в БД", status_code=status.HTTP_200_OK
)
async def update_goods(
    good: GoodFromUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    good_id: Annotated[int, Path(...)],
):
    response = await update_good(good_id, good, db)
    return GoodAnswer(
        name=response,
        description="Информация о товаре успешно обновлена",
    )


@router.patch("/goods_quantity", summary="Обновляет количество товара")
async def update_good_stock_quantity(
    goods_quantity: Annotated[int, Query(...)],
    product_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    await update_stock_quantity(product_id, goods_quantity, db)
    return GoodAnswerId(
        id=product_id,
        description="Количество товара обновлено",
    )


@router.delete(
    "/{product_id}", summary="Удлаяет товар из БД по id", status_code=status.HTTP_200_OK
)
async def del_product(
    product_id: Annotated[int, Path(...)], db: Annotated[AsyncSession, Depends(get_db)]
):
    response = await delete_product_by_id(product_id, db)
    return response
