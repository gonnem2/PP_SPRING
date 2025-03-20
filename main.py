from fastapi import FastAPI

from routers.user.user_router import router
from routers.good.good import router as good_router


app = FastAPI(title="Best Project in the world")

app.include_router(router)
app.include_router(good_router)
