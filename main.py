from fastapi import FastAPI

from routers.user.user_router import router


app = FastAPI(title="Best Project in the world")

app.include_router(router)


@app.get("/say_hello_world")
def say_hello():
    return "Hello World!!"
