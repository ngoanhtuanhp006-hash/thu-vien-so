import os
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from database import get_db
from models import Book, Copy, Loan, Fine, User
from schemas import LoanIn, LoanOut
from security import get_current_user, require_librarian

load_dotenv()

FINE_PER_DAY = int(os.getenv("FINE_PER_DAY", "2000"))
LOAN_DAYS = int(os.getenv("LOAN_DAYS", "14"))
MAX_LOANS = 3

router = APIRouter(tags=["Loans"])


def as_date(x):
    return x.date() if isinstance(x, datetime) else x


def overdue_days(loan: Loan) -> int:
    if not loan.due_date or loan.status == "requested":
        return 0
    end = as_date(loan.returned_at) if loan.returned_at else datetime.now(timezone.utc).date()
    return max(0, (end - as_date(loan.due_date)).days)


def loan_out(db: Session, loan: Loan) -> dict:
    copy = db.get(Copy, loan.copy_id)
    book = db.get(Book, copy.book_id)
    fine = db.scalar(select(Fine).where(Fine.loan_id == loan.id))
    days = overdue_days(loan)
    amount = int(fine.amount) if fine else days * FINE_PER_DAY
    return {
        "id": loan.id, "user_id": loan.user_id, "copy_id": loan.copy_id,
        "book_title": book.title, "barcode": copy.barcode,
        "status": loan.status, "requested_at": loan.requested_at,
        "borrowed_at": loan.borrowed_at, "due_date": loan.due_date,
        "returned_at": loan.returned_at,
        "overdue_days": days, "fine_amount": amount,
    }


# ---------- Ban doc dat muon ----------
@router.post("/loans", response_model=LoanOut, status_code=201)
def request_loan(data: LoanIn, db: Session = Depends(get_db),
                 user: User = Depends(get_current_user)):
    if not db.get(Book, data.book_id):
        raise HTTPException(404, "Khong tim thay sach")

    active = db.scalar(
        select(func.count()).select_from(Loan)
        .where(Loan.user_id == user.id,
               Loan.status.in_(["requested", "borrowed"]))
    )
    if active >= MAX_LOANS:
        raise HTTPException(409, f"Moi ban doc chi duoc muon toi da {MAX_LOANS} cuon")

    copy = db.scalar(
        select(Copy)
        .where(Copy.book_id == data.book_id, Copy.status == "available")
        .limit(1).with_for_update(skip_locked=True)
    )
    if not copy:
        raise HTTPException(409, "Sach da het ban")

    copy.status = "reserved"
    loan = Loan(user_id=user.id, copy_id=copy.id, status="requested",
                requested_at=datetime.now(timezone.utc))
    db.add(loan)
    db.commit()
    db.refresh(loan)
    return loan_out(db, loan)


@router.get("/me/loans", response_model=list[LoanOut])
def my_loans(db: Session = Depends(get_db),
             user: User = Depends(get_current_user)):
    loans = db.scalars(select(Loan).where(Loan.user_id == user.id)
                       .order_by(Loan.id.desc())).all()
    return [loan_out(db, l) for l in loans]


# ---------- Thu thu ----------
@router.get("/loans", response_model=list[LoanOut],
            dependencies=[Depends(require_librarian)])
def all_loans(status: str | None = None, db: Session = Depends(get_db)):
    stmt = select(Loan).order_by(Loan.id.desc())
    if status:
        stmt = stmt.where(Loan.status == status)
    return [loan_out(db, l) for l in db.scalars(stmt).all()]


@router.post("/loans/{loan_id}/checkout", response_model=LoanOut,
             dependencies=[Depends(require_librarian)])
def checkout(loan_id: int, db: Session = Depends(get_db)):
    loan = db.get(Loan, loan_id)
    if not loan:
        raise HTTPException(404, "Khong tim thay phieu muon")
    if loan.status != "requested":
        raise HTTPException(409, "Phieu nay khong o trang thai cho giao sach")
    now = datetime.now(timezone.utc)
    loan.borrowed_at = now
    loan.due_date = now + timedelta(days=LOAN_DAYS)
    loan.status = "borrowed"
    db.get(Copy, loan.copy_id).status = "borrowed"
    db.commit()
    db.refresh(loan)
    return loan_out(db, loan)


@router.post("/loans/{loan_id}/return", response_model=LoanOut,
             dependencies=[Depends(require_librarian)])
def return_book(loan_id: int, db: Session = Depends(get_db)):
    loan = db.get(Loan, loan_id)
    if not loan:
        raise HTTPException(404, "Khong tim thay phieu muon")
    if loan.status != "borrowed":
        raise HTTPException(409, "Phieu nay chua duoc giao sach hoac da tra")
    loan.returned_at = datetime.now(timezone.utc)
    loan.status = "returned"
    db.get(Copy, loan.copy_id).status = "available"

    days = overdue_days(loan)
    if days > 0:
        db.add(Fine(loan_id=loan.id, amount=days * FINE_PER_DAY, paid=False))
    db.commit()
    db.refresh(loan)
    return loan_out(db, loan)