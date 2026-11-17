from datetime import datetime, date
from sqlalchemy import (
    String, Integer, Text, DateTime, Date, Boolean, Numeric,
    ForeignKey, Table, Column,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base

# Bảng trung gian: quan hệ N:N giữa sách và tác giả
book_authors = Table(
    "book_authors",
    Base.metadata,
    Column("book_id", ForeignKey("books.id"), primary_key=True),
    Column("author_id", ForeignKey("authors.id"), primary_key=True),
)


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(20), default="reader")  # reader / librarian
    loans: Mapped[list["Loan"]] = relationship(back_populates="user")


class Author(Base):
    __tablename__ = "authors"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    books: Mapped[list["Book"]] = relationship(
        secondary=book_authors, back_populates="authors"
    )


class Category(Base):
    __tablename__ = "categories"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True)
    books: Mapped[list["Book"]] = relationship(back_populates="category")


class Book(Base):
    __tablename__ = "books"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    isbn: Mapped[str | None] = mapped_column(String(20), unique=True)
    description: Mapped[str | None] = mapped_column(Text)
    cover_url: Mapped[str | None] = mapped_column(String(255))
    category_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id"))
    category: Mapped["Category"] = relationship(back_populates="books")
    authors: Mapped[list["Author"]] = relationship(
        secondary=book_authors, back_populates="books"
    )
    copies: Mapped[list["Copy"]] = relationship(back_populates="book")


class Copy(Base):
    __tablename__ = "copies"
    id: Mapped[int] = mapped_column(primary_key=True)
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id"))
    barcode: Mapped[str] = mapped_column(String(50), unique=True)
    status: Mapped[str] = mapped_column(String(20), default="available")
    book: Mapped["Book"] = relationship(back_populates="copies")
    loans: Mapped[list["Loan"]] = relationship(back_populates="copy")


class Loan(Base):
    __tablename__ = "loans"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    copy_id: Mapped[int] = mapped_column(ForeignKey("copies.id"))
    status: Mapped[str] = mapped_column(String(20), default="requested")
    requested_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    borrowed_at: Mapped[datetime | None] = mapped_column(DateTime)
    due_date: Mapped[date | None] = mapped_column(Date)
    returned_at: Mapped[datetime | None] = mapped_column(DateTime)
    user: Mapped["User"] = relationship(back_populates="loans")
    copy: Mapped["Copy"] = relationship(back_populates="loans")
    fine: Mapped["Fine | None"] = relationship(back_populates="loan")


class Fine(Base):
    __tablename__ = "fines"
    id: Mapped[int] = mapped_column(primary_key=True)
    loan_id: Mapped[int] = mapped_column(ForeignKey("loans.id"))
    amount: Mapped[float] = mapped_column(Numeric(10, 2))
    paid: Mapped[bool] = mapped_column(Boolean, default=False)
    loan: Mapped["Loan"] = relationship(back_populates="fine")