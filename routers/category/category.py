from typing import Annotated

from fastapi import APIRouter, Depends, status, Path

from sqlalchemy.ext.asyncio import AsyncSession

from backend.db import get_db
from crud.category.category_crud import (
    create_category,
    get_categories,
    get_category_by_id,
    put_category_by_id,
    delete_category,
)
from routers.auth.utils import get_current_user
from schemas.requests.CategoryRequest import CategoryRequest
from schemas.requests.pagination import PaginationParams
from schemas.response.category_for_user import CategoryResponse

router = APIRouter(tags=["Категории товаров"], prefix="/category")


@router.post(
    "",
    summary="Создание категории",
    description="Принимает через Body категорию",
    status_code=status.HTTP_201_CREATED,
)
async def create_category_endpoint(
    db: Annotated[AsyncSession, Depends(get_db)],
    category_from_user: CategoryRequest,
    current_user: Annotated[dict, Depends(get_current_user)],
):
    if await create_category(db, category_from_user, current_user):
        return {
            "detail": f"Категория {category_from_user.name} успешно создана",
        }


@router.get(
    "/{category_id}",
    summary="Возвращает категорию по id",
    status_code=status.HTTP_200_OK,
)
async def get_category_by_id_endpoint(
    category_id: Annotated[int, Path(gt=0)],
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
) -> CategoryResponse:
    if category := await get_category_by_id(category_id, db):
        return CategoryResponse.from_orm(category)


@router.get(
    "",
    summary="Возвращает категории",
    description="Принимает 2 q параметра: страница"
    " и кол-во элементов т.е. страница * кол-во",
    status_code=status.HTTP_200_OK,
)
async def get_all_categories_endpoint(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
    pagination: Annotated[PaginationParams, Depends()],
):
    if categories := await get_categories(db, pagination):
        return categories


@router.put(
    "/{category_id}", summary="Меняет категорию по id", status_code=status.HTTP_200_OK
)
async def put_category_by_id_endpoint(
    category_id: Annotated[int, Path(gt=0)],
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
    category: CategoryRequest,
):
    if await put_category_by_id(db, category_id, category):
        return {"detail": "Категория успешно изменена!"}


@router.delete(
    "/{category_id}",
    status_code=status.HTTP_200_OK,
    summary="Удаляет категорию вместе со всеми товарами и под категориями",
)
async def delete_category_endpoint(
    db: Annotated[AsyncSession, Depends(get_db)],
    category_id: int,
    current_user: Annotated[dict, Depends(get_current_user)],
):
    if await delete_category(db, category_id, current_user):
        return {"detail": "Категория успешно удалена"}
