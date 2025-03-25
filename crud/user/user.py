from fastapi import HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext

from models.user import User
from crud.user.utils import get_user_by_email, get_user_by_username
from schemas.requests.user_from_user import CreateUser
from schemas.response.user_for_user import UserGet


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def create_user(db: AsyncSession, user: CreateUser):
    if await get_user_by_email(db, user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email уже существует",
        )
    if await get_user_by_username(db, user.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким username уже существует",
        )

    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=pwd_context.hash(user.password),
        first_name=user.first_name,
        last_name=user.last_name,
    )
    db.add(db_user)
    await db.commit()
    return UserGet(name=user.username, message="Пользователь успешно создан!")
