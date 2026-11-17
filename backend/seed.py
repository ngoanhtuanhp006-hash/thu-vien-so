from database import SessionLocal
from models import User, Category, Author
from security import hash_password
from sqlalchemy import select

db = SessionLocal()

if not db.scalar(select(User).where(User.email == "thuthu@example.com")):
    db.add(User(email="thuthu@example.com",
                password_hash=hash_password("thuthu123"),
                full_name="Thu Thu Khoa CNTT",
                role="librarian"))

for name in ["Lap trinh", "Co so du lieu", "Mang may tinh"]:
    if not db.scalar(select(Category).where(Category.name == name)):
        db.add(Category(name=name))

for name in ["Robert C. Martin", "Abraham Silberschatz"]:
    if not db.scalar(select(Author).where(Author.name == name)):
        db.add(Author(name=name))

db.commit()
db.close()
print("Seed xong")