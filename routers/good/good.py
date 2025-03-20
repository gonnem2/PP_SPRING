from datetime import datetime, timedelta, date
from typing import Annotated

from fastapi import APIRouter, status, Path

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
    get_prod_stat,
)
from schemas.requests.good_from_user import GoodFromUser
from schemas.response.GoodStatistic import GoodStat
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
    min_price: Annotated[int, Query(ge=0)] = 0,
    max_price: Annotated[int, Query(ge=1)] = None,
    min_stock_quantity: Annotated[int, Query(ge=0)] = None,
    max_stock_quantity: Annotated[int, Query(ge=0)] = None,
):
    products_from_db = await get_products_by_category(
        category_id, db, min_price, max_price, min_stock_quantity, max_stock_quantity
    )

    return products_from_db


@router.get("/by_id/{product_id}", summary="Возвращает товар по id")
async def get_prod_by_id(
    product_id: Annotated[int, Path(...)], db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Возвращает товар в БД по id

    Args:
        product_id (int): id товара
        db (AsyncSession): генератор сессий с БД

    Returns:
        dict: информация о товаре

    Raises:
        HttpException: 404, если товар не найден
    """

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
async def get_goods(
    db: Annotated[AsyncSession, Depends(get_db)],
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1)] = 100,
):
    """
    Возвращает список всех товаров

    Args:
        db (AsyncSession): объект сессии бд
        skip (int): От какого по счету товара возвращать (по умолчанию 0)
        limit (int): До какого товара возвращать (по умолчанию 100)

    Returns:
        list[dict]: Список товаров

    Raises:
        HttpException: 404 если товары не найдены
    """

    data = await get_all_goods(db, skip, limit)
    return data


@router.get(
    "/by_name",
    summary="Ищет товар по части имени и если нашел, то возвращает его",
    status_code=status.HTTP_200_OK,
)
async def get_good_by_name(
    name: Annotated[str, Query(...)], db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Возвращает товар. чье имя наиболее похоже на введенное

    Args:
        name (str): Имя товара
        db (AsyncSession): Сессия с БД

    Returns:
        dict: JSON информация о товаре

    Raises:
        HttpExcepion: 404, если товар не найден
    """

    data = await get_goods_by_name(db, name.strip())
    return data


@router.post("/", summary="Добавить товар", status_code=status.HTTP_201_CREATED)
async def add_new_good(
    good: GoodFromUser, db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Добавляет товар в БД

    Args:
        good (GoodFromUser): объект с атрибутами товара
        db (AsyncSession): Сессия с БД

    Returns:
        str: Информмация об успешном создании товара

    Raises:
        HttpExcepion: 400, если переданной категории товара не сущесвует
    """

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
    """
    Обновляет товар в БД

     Args:
         good (str): объект с информацией о товаре
         db (AsyncSession): Сессия с БД
         good_id (int): id товара, который нужно заменить

     Returns:
         GoodAnswer: объект с именеи товара и сообщением об успешном обновлении

     Raises:
         HttpExcepion: 404, если товар с переданным id не найден
    """

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
    """
    Обновляет количество товара

    Args:
        goods_quantity (int): количество товара, которое нужно добавить
        product_id (int): id обновляемого товара
        db (AsyncSession): сессия Бд

    Returns:
        GoodAnswerId: id товара и описание операции

    Raises:
        HTTPException: 404, если товар с переданным id не найден

    """
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
    """
    Удаляет товар

    Args:
        product_id (int): id удаляемого товара
        db (AsyncSession): сессия Бд

    Returns:
        str: "Товар успешно удален"

    Raises:
        HTTPException: 404, если товар с переданным id не найден

    """

    response = await delete_product_by_id(product_id, db)
    return response


@router.get(
    "/statistic/{product_id}",
    summary="Возвращает статистику по товару",
    status_code=status.HTTP_200_OK,
    response_model=GoodStat,
)
async def get_product_statistic(
    db: Annotated[AsyncSession, Depends(get_db)],
    product_id: Annotated[int, Path(...)],
    start_date: Annotated[datetime, Query(...)] = datetime.now() - timedelta(days=30),
    end_date: Annotated[datetime, Query()] = datetime.now(),
):
    """Возвращает статистику по товару за указанный период.

    Args:
        db (AsyncSession): Сессия базы данных.
        product_id (int): ID товара.
        start_date (datetime): Дата начала периода (по умолчанию — 30 дней назад).
        end_date (datetime): Дата окончания периода (по умолчанию — текущая дата).

    Returns:
        GoodStat: Статистика по товару.

    Raises:
        HTTPException 400: Если start_date > end_date.
        HTTPException 404: Если товар не найден.
        HTTPException 500: Если произошла внутренняя ошибка сервера.
    """

    response = await get_prod_stat(db, product_id, start_date, end_date)
    return response
