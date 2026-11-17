import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from database import get_db
from models import Book, Copy, Loan
from security import require_librarian

router = APIRouter()

UPLOAD_DIR = Path(__file__).parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_TYPES = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}
MAX_SIZE = 2 * 1024 * 1024  # 2 MB


@router.post("/books/{book_id}/cover", tags=["Books"],
             dependencies=[Depends(require_librarian)])
async def upload_cover(book_id: int, file: UploadFile = File(...),
                       db: Session = Depends(get_db)):
    book = db.get(Book, book_id)
    if not book:
        raise HTTPException(404, "Khong tim thay sach")
    ext = ALLOWED_TYPES.get(file.content_type)
    if not ext:
        raise HTTPException(415, "Chi nhan anh JPG, PNG hoac WEBP")
    content = await file.read()
    if len(content) > MAX_SIZE:
        raise HTTPException(413, "Anh qua lon, toi da 2 MB")
    name = f"{uuid.uuid4().hex}{ext}"
    (UPLOAD_DIR / name).write_bytes(content)
    book.cover_url = f"/uploads/{name}"
    db.commit()
    return {"cover_url": book.cover_url}


@router.get("/stats/top-books", tags=["Stats"],
            dependencies=[Depends(require_librarian)])
def top_books(limit: int = Query(5, ge=1, le=20),
              db: Session = Depends(get_db)):
    rows = db.execute(
        select(Book.id, Book.title, func.count(Loan.id).label("borrow_count"))
        .join(Copy, Copy.book_id == Book.id)
        .join(Loan, Loan.copy_id == Copy.id)
        .where(Loan.status.in_(["borrowed", "returned"]))
        .group_by(Book.id, Book.title)
        .order_by(func.count(Loan.id).desc())
        .limit(limit)
    ).all()
    return [{"book_id": r.id, "title": r.title,
             "borrow_count": r.borrow_count} for r in rows]