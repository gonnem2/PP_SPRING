import os
from datetime import timedelta

from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, status

from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select, update

from models import User
from routers.auth.utils import create_access_token, get_current_user
from crud.user.utils import authenticate_user
from schemas.response.jwt_token import Token
from typing import Annotated


from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db import get_db

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/token")
async def token(
    db: Annotated[AsyncSession, Depends(get_db)],
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
):
    user = await authenticate_user(db, form_data.username, form_data.password)

    token_res = Token(
        access_token=await create_access_token(
            username=user.username,
            user_id=user.id,
            is_owner=user.is_owner,
            is_seller=user.is_seller,
            is_warehouse_worker=user.is_warehouse_worker,
            expires_delta=timedelta(minutes=30),
        ),
        token_type="bearer",
    )
    return token_res
