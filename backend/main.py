from fastapi import FastAPI

app = FastAPI(title="Thu vien so Khoa CNTT")

@app.get("/")
def hello():
    return {"message": "Xin chao, thu vien so dang chay!"}