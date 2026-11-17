from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, delete, insert
from sqlalchemy.orm import Session

from database import get_db
from models import Book, Author, Category, Copy, book_authors
from schemas import (AuthorIn, AuthorOut, CategoryIn, CategoryOut,
                     BookIn, BookOut, BookPage, CopyIn, CopyOut)
from security import require_librarian

router = APIRouter()


def to_out(db: Session, b: Book) -> dict:
    authors = db.scalars(
        select(Author)
        .join(book_authors, book_authors.c.author_id == Author.id)
        .where(book_authors.c.book_id == b.id)
    ).all()
    category = db.get(Category, b.category_id) if b.category_id else None
    available = db.scalar(
        select(func.count()).select_from(Copy)
        .where(Copy.book_id == b.id, Copy.status == "available")
    )
    return {"id": b.id, "title": b.title, "isbn": b.isbn,
            "description": b.description, "cover_url": b.cover_url,
            "category": category, "authors": authors,
            "available_copies": available}


def set_authors(db: Session, book_id: int, author_ids: list[int]):
    db.execute(delete(book_authors).where(book_authors.c.book_id == book_id))
    for aid in set(author_ids):
        if not db.get(Author, aid):
            raise HTTPException(404, f"Khong co tac gia id={aid}")
        db.execute(insert(book_authors).values(book_id=book_id, author_id=aid))


# ---------- Tac gia ----------
@router.get("/authors", response_model=list[AuthorOut], tags=["Authors"])
def list_authors(db: Session = Depends(get_db)):
    return db.scalars(select(Author).order_by(Author.name)).all()


@router.post("/authors", response_model=AuthorOut, status_code=201,
             tags=["Authors"], dependencies=[Depends(require_librarian)])
def create_author(data: AuthorIn, db: Session = Depends(get_db)):
    a = Author(name=data.name)
    db.add(a)
    db.commit()
    db.refresh(a)
    return a


# ---------- Chu de ----------
@router.get("/categories", response_model=list[CategoryOut], tags=["Categories"])
def list_categories(db: Session = Depends(get_db)):
    return db.scalars(select(Category).order_by(Category.name)).all()


@router.post("/categories", response_model=CategoryOut, status_code=201,
             tags=["Categories"], dependencies=[Depends(require_librarian)])
def create_category(data: CategoryIn, db: Session = Depends(get_db)):
    c = Category(name=data.name)
    db.add(c)
    db.commit()
    db.refresh(c)
    return c


# ---------- Sach ----------
@router.get("/books", response_model=BookPage, tags=["Books"])
def search_books(
    q: str | None = None,
    author: str | None = None,
    category_id: int | None = None,
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    stmt = select(Book)
    if q:
        stmt = stmt.where(Book.title.ilike(f"%{q}%"))
    if category_id:
        stmt = stmt.where(Book.category_id == category_id)
    if author:
        stmt = (
            stmt.join(book_authors, book_authors.c.book_id == Book.id)
            .join(Author, Author.id == book_authors.c.author_id)
            .where(Author.name.ilike(f"%{author}%"))
            .distinct()
        )
    total = db.scalar(select(func.count()).select_from(stmt.subquery()))
    books = db.scalars(
        stmt.order_by(Book.id).offset((page - 1) * size).limit(size)
    ).all()
    return {"total": total, "page": page, "size": size,
            "items": [to_out(db, b) for b in books]}


@router.get("/books/{book_id}", response_model=BookOut, tags=["Books"])
def get_book(book_id: int, db: Session = Depends(get_db)):
    b = db.get(Book, book_id)
    if not b:
        raise HTTPException(404, "Khong tim thay sach")
    return to_out(db, b)


@router.post("/books", response_model=BookOut, status_code=201,
             tags=["Books"], dependencies=[Depends(require_librarian)])
def create_book(data: BookIn, db: Session = Depends(get_db)):
    b = Book(title=data.title, isbn=data.isbn,
             description=data.description, category_id=data.category_id)
    db.add(b)
    db.flush()
    set_authors(db, b.id, data.author_ids)
    db.commit()
    db.refresh(b)
    return to_out(db, b)


@router.put("/books/{book_id}", response_model=BookOut, tags=["Books"],
            dependencies=[Depends(require_librarian)])
def update_book(book_id: int, data: BookIn, db: Session = Depends(get_db)):
    b = db.get(Book, book_id)
    if not b:
        raise HTTPException(404, "Khong tim thay sach")
    b.title, b.isbn = data.title, data.isbn
    b.description, b.category_id = data.description, data.category_id
    set_authors(db, b.id, data.author_ids)
    db.commit()
    db.refresh(b)
    return to_out(db, b)


@router.delete("/books/{book_id}", status_code=204, tags=["Books"],
               dependencies=[Depends(require_librarian)])
def delete_book(book_id: int, db: Session = Depends(get_db)):
    b = db.get(Book, book_id)
    if not b:
        raise HTTPException(404, "Khong tim thay sach")
    db.execute(delete(book_authors).where(book_authors.c.book_id == b.id))
    db.delete(b)
    db.commit()


# ---------- Ban sach (ma vach) ----------
@router.post("/copies", response_model=CopyOut, status_code=201,
             tags=["Copies"], dependencies=[Depends(require_librarian)])
def create_copy(data: CopyIn, db: Session = Depends(get_db)):
    if not db.get(Book, data.book_id):
        raise HTTPException(404, "Khong tim thay sach")
    if db.scalar(select(Copy).where(Copy.barcode == data.barcode)):
        raise HTTPException(409, "Ma vach da ton tai")
    c = Copy(book_id=data.book_id, barcode=data.barcode, status="available")
    db.add(c)
    db.commit()
    db.refresh(c)
    return c


@router.get("/books/{book_id}/copies", response_model=list[CopyOut],
            tags=["Copies"], dependencies=[Depends(require_librarian)])
def list_copies(book_id: int, db: Session = Depends(get_db)):
    return db.scalars(select(Copy).where(Copy.book_id == book_id)).all()