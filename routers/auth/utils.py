from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from dotenv import load_dotenv
import os

from fastapi import Depends, HTTPException, status

from routers.auth.security import oauth2_scheme

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")


async def create_access_token(
    username: str,
    user_id: int,
    is_owner: bool,
    is_seller: bool,
    is_warehouse_worker: bool,
    expires_delta: timedelta,
):
    payload = {
        "sub": username,
        "id": user_id,
        "is_owner": is_owner,
        "is_seller": is_seller,
        "is_warehouse_worker": is_warehouse_worker,
        "exp": int((datetime.now(timezone.utc) + expires_delta).timestamp()),
    }
    return jwt.encode(payload, SECRET_KEY, ALGORITHM)


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str | None = payload.get("sub")
        user_id: int | None = payload.get("id")
        is_owner: bool | None = payload.get("is_owner")
        is_seller: bool | None = payload.get("is_seller")
        is_warehouse_worker: bool | None = payload.get("is_warehouse_worker")
        expire: int | None = payload.get("exp")

        if username is None or user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate user",
            )
        if expire is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No access token supplied",
            )

        if not isinstance(expire, int):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token format"
            )

        # Проверка срока действия токена
        current_time = datetime.now(timezone.utc).timestamp()

        if expire < current_time:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired!"
            )

        return {
            "username": username,
            "id": user_id,
            "is_owner": is_owner,
            "is_seller": is_seller,
            "is_warehouse_worker": is_warehouse_worker,
        }
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired!"
        )
    except jwt.exceptions:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user"
        )
