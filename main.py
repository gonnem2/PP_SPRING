from fastapi import FastAPI

from routers.user.user_router import router
from routers.good.good import router as good_router
from routers.auth.auth import router as token_router
from routers.cash.cash import router as cash_router
from routers.permission.permission import router as permission_router
from routers.category.category import router as category_router


app = FastAPI(title="Best Project in the world")

app.include_router(router)
app.include_router(good_router)
app.include_router(token_router)
app.include_router(cash_router)
app.include_router(permission_router)
app.include_router(category_router)
