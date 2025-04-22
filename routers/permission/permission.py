from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy import select, update

from sqlalchemy.ext.asyncio import AsyncSession

from models import User
from routers.auth.utils import get_current_user
from schemas.requests.permission_from_user import PermissionSet
from typing import Annotated
from backend.db import get_db
from schemas.response.permission_set_for_user import PermissionResponse


router = APIRouter(prefix="/permission", tags=["Права доступа"])


@router.patch(
    "/change_permission",
    response_model=PermissionResponse,
    status_code=status.HTTP_200_OK,
    summary="Изменяет уровень доступа пользователя",
)
async def change_user_permission(
    db: Annotated[AsyncSession, Depends(get_db)],
    user_id: int,
    current_user: Annotated[dict, Depends(get_current_user)],
    permission_status: PermissionSet,
):
    if not current_user.get("is_owner", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="У вас нет доступа",
        )

    if not (user_from_db := await db.scalar(select(User).where(User.id == user_id))):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь с таким id не найден",
        )

    await db.execute(
        update(User)
        .where(User.id == user_id)
        .values(
            is_owner=permission_status.set_owner,
            is_seller=permission_status.set_seller,
            is_warehouse_worker=permission_status.set_warehouse_worker,
        )
    )

    await db.commit()

    return PermissionResponse(
        user_id=user_id,
        message=f"Статус пользователя"
        f" успешно изменен на"
        f" {"Owner" * permission_status.set_owner +
            "Warehouse_worker" * permission_status.set_warehouse_worker
            + "Seller" * permission_status.set_seller}",
    )
