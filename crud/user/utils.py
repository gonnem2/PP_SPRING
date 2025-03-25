from typing import Annotated

from dotenv import load_dotenv
import os

from fastapi import Depends, HTTPException, status
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db import get_db
from models import User

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(password_from_user, password_from_db):
    return pwd_context.verify(password_from_user, password_from_db)


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.scalars(select(User).where(User.email == email))
    return result.first()


async def get_user_by_username(db: AsyncSession, username: str):
    result = await db.scalars(select(User).where(User.username == username))

    return result.first()


async def authenticate_user(
    db: Annotated[AsyncSession, Depends(get_db)], username: str, password: str
):
    if not (user := await get_user_by_username(db, username)):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователя с таким username не найден",
        )

    if not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Пароль неправильный!"
        )

    return user
