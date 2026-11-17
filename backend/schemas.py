from pydantic import BaseModel, EmailStr, ConfigDict


class RegisterIn(BaseModel):
    email: EmailStr
    password: str
    full_name: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: str
    full_name: str
    role: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    class AuthorIn(BaseModel):
    name: str

class AuthorOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str

class CategoryIn(BaseModel):
    name: str

class CategoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str

class BookIn(BaseModel):
    title: str
    isbn: str | None = None
    description: str | None = None
    category_id: int | None = None
    author_ids: list[int] = []

class BookOut(BaseModel):
    id: int
    title: str
    isbn: str | None
    description: str | None
    cover_url: str | None
    category: CategoryOut | None
    authors: list[AuthorOut]
    available_copies: int

class BookPage(BaseModel):
    total: int
    page: int
    size: int
    items: list[BookOut]

class CopyIn(BaseModel):
    book_id: int
    barcode: str

class CopyOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    book_id: int
    barcode: str
    status: str