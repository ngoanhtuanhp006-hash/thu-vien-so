from datetime import datetime

import routers_loans


# ---------- Xac thuc ----------
def test_register_and_me(client, reader):
    r = client.get("/me", headers=reader)
    assert r.status_code == 200
    assert r.json()["email"] == "an@test.com"
    assert r.json()["role"] == "reader"


def test_register_duplicate_email(client, reader):
    r = client.post("/auth/register", json={
        "email": "an@test.com", "password": "123456", "full_name": "An"})
    assert r.status_code in (400, 409)


def test_login_wrong_password(client, reader):
    r = client.post("/auth/login",
                    data={"username": "an@test.com", "password": "sai"})
    assert r.status_code in (400, 401)


def test_me_requires_token(client):
    assert client.get("/me").status_code == 401


# ---------- Phan quyen ----------
def test_reader_cannot_create_book(client, reader):
    r = client.post("/books", json={"title": "X"}, headers=reader)
    assert r.status_code == 403


def test_reader_cannot_checkout(client, reader, make_book):
    make_book()
    loan = client.post("/loans", json={"book_id": 1}, headers=reader).json()
    r = client.post(f"/loans/{loan['id']}/checkout", headers=reader)
    assert r.status_code == 403


# ---------- Sach ----------
def test_librarian_create_and_search_book(client, librarian, make_book):
    make_book("Clean Code", copies=2)
    r = client.get("/books", params={"q": "clean"})
    assert r.status_code == 200
    body = r.json()
    assert body["total"] == 1
    assert body["items"][0]["available_copies"] == 2


def test_duplicate_barcode_returns_409(client, librarian, make_book):
    book_id = make_book(copies=1)
    r = client.post("/copies", json={"book_id": book_id, "barcode": f"BC-{book_id}-1"},
                    headers=librarian)
    assert r.status_code == 409


def test_book_not_found(client):
    assert client.get("/books/999").status_code == 404


# ---------- Muon tra ----------
def test_request_loan_and_out_of_stock(client, reader, make_book):
    book_id = make_book(copies=1)
    r1 = client.post("/loans", json={"book_id": book_id}, headers=reader)
    assert r1.status_code == 201
    assert r1.json()["status"] == "requested"
    r2 = client.post("/loans", json={"book_id": book_id}, headers=reader)
    assert r2.status_code == 409


def test_max_three_loans(client, reader, make_book):
    ids = [make_book(f"Sach {i}") for i in range(4)]
    for i in ids[:3]:
        assert client.post("/loans", json={"book_id": i}, headers=reader).status_code == 201
    r = client.post("/loans", json={"book_id": ids[3]}, headers=reader)
    assert r.status_code == 409


def test_full_loan_flow_no_fine(client, reader, librarian, make_book):
    book_id = make_book()
    loan = client.post("/loans", json={"book_id": book_id}, headers=reader).json()
    r = client.post(f"/loans/{loan['id']}/checkout", headers=librarian)
    assert r.json()["status"] == "borrowed"
    assert r.json()["due_date"] is not None
    r = client.post(f"/loans/{loan['id']}/return", headers=librarian)
    assert r.json()["status"] == "returned"
    assert r.json()["fine_amount"] == 0


def test_overdue_fine(client, reader, librarian, make_book, monkeypatch):
    monkeypatch.setattr(routers_loans, "LOAN_DAYS", -3)
    book_id = make_book()
    loan = client.post("/loans", json={"book_id": book_id}, headers=reader).json()
    client.post(f"/loans/{loan['id']}/checkout", headers=librarian)
    r = client.post(f"/loans/{loan['id']}/return", headers=librarian)
    assert r.json()["overdue_days"] == 3
    assert r.json()["fine_amount"] == 3 * routers_loans.FINE_PER_DAY


def test_my_loans_history(client, reader, make_book):
    book_id = make_book()
    client.post("/loans", json={"book_id": book_id}, headers=reader)
    r = client.get("/me/loans", headers=reader)
    assert r.status_code == 200
    assert len(r.json()) == 1