from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from routers_auth import router as auth_router
from routers_books import router as books_router
from routers_loans import router as loans_router
from routers_extra import router as extra_router, UPLOAD_DIR

app = FastAPI(title="Thu vien so Khoa CNTT")
app.include_router(auth_router)
app.include_router(books_router)
app.include_router(loans_router)
app.include_router(extra_router)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")


@app.get("/")
def hello():
    return {"message": "Xin chao, thu vien so dang chay!"}