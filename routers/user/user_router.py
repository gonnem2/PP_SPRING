from fastapi import APIRouter, Depends, status
from typing import Annotated
from sqlalchemy import select

from sqlalchemy.ext.asyncio import AsyncSession

from backend.db import get_db
from models.user import User
from schemas.requests.user_from_user import CreateUser
from crud.user.user import create_user
from schemas.response.user_for_user import UserGet

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
