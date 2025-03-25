from fastapi import APIRouter, Depends, status
from typing import Annotated
from sqlalchemy import select

from sqlalchemy.ext.asyncio import AsyncSession

from backend.db import get_db
from models import Notification
from models.user import User
from routers.auth.utils import get_current_user
from schemas.requests.user_from_user import CreateUser
from crud.user.user import create_user

router = APIRouter(tags=["Обработка пользователя"], prefix="/user")


@router.get("/")
async def get_all_users(db: Annotated[AsyncSession, Depends(get_db)]):
    users = await db.scalars(select(User))
    return users.all()


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user_endpoint(
    db: Annotated[AsyncSession, Depends(get_db)], user: CreateUser
):
    new_user = await create_user(db, user)
    return new_user


@router.get("/current_user")
async def current_user(user: Annotated[dict, Depends(get_current_user)]):
    return user
