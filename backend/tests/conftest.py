import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database import Base, get_db
from main import app
from models import User
from security import hash_password

engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def override_get_db():
    db = TestingSession()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def fresh_db():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    yield


@pytest.fixture
def client():
    return TestClient(app)


def login(client, email, password):
    r = client.post("/auth/login", data={"username": email, "password": password})
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


@pytest.fixture
def librarian(client):
    db = TestingSession()
    db.add(User(email="thuthu@test.com", password_hash=hash_password("thuthu123"),
                full_name="Thu Thu", role="librarian"))
    db.commit()
    db.close()
    return login(client, "thuthu@test.com", "thuthu123")


@pytest.fixture
def reader(client):
    client.post("/auth/register", json={
        "email": "an@test.com", "password": "123456", "full_name": "An"})
    return login(client, "an@test.com", "123456")


@pytest.fixture
def make_book(client, librarian):
    """Tao 1 dau sach kem n ban, tra ve book_id."""
    counter = {"n": 0}

    def _make(title="Clean Code", copies=1):
        r = client.post("/books", json={"title": title}, headers=librarian)
        assert r.status_code == 201, r.text
        book_id = r.json()["id"]
        for _ in range(copies):
            counter["n"] += 1
            r = client.post("/copies", json={
                "book_id": book_id, "barcode": f"BC-{book_id}-{counter['n']}"},
                headers=librarian)
            assert r.status_code == 201, r.text
        return book_id

    return _make