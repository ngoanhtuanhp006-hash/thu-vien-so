from fastapi import FastAPI
from routers_auth import router as auth_router
from routers_books import router as books_router

app = FastAPI(title="Thu vien so Khoa CNTT")
app.include_router(auth_router)
app.include_router(books_router)


@app.get("/")
def hello():
    return {"message": "Xin chao, thu vien so dang chay!"}