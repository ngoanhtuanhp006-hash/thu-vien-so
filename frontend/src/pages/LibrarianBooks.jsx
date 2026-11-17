import { useEffect, useState } from "react";
import { api, API } from "../api";

const JSON_HEADER = { "Content-Type": "application/json" };

export default function LibrarianBooks() {
  const [books, setBooks] = useState([]);
  const [authors, setAuthors] = useState([]);
  const [categories, setCategories] = useState([]);
  const [form, setForm] = useState({ title: "", isbn: "", category_id: "", author_ids: [] });
  const [newAuthor, setNewAuthor] = useState("");
  const [newCategory, setNewCategory] = useState("");
  const [barcodes, setBarcodes] = useState({});
  const [msg, setMsg] = useState("");
  const [error, setError] = useState("");

  async function loadAll() {
    try {
      const b = await api("/books?size=50");
      setBooks(b.items);
      setAuthors(await api("/authors"));
      setCategories(await api("/categories"));
    } catch (e) {
      setError(e.message);
    }
  }

  useEffect(() => {
    loadAll();
  }, []);

  async function run(fn, okMsg) {
    setMsg("");
    setError("");
    try {
      await fn();
      setMsg(okMsg);
      await loadAll();
    } catch (e) {
      setError(e.message);
    }
  }

  const createBook = (e) => {
    e.preventDefault();
    run(async () => {
      await api("/books", {
        method: "POST",
        headers: JSON_HEADER,
        body: JSON.stringify({
          title: form.title,
          isbn: form.isbn || null,
          category_id: form.category_id ? Number(form.category_id) : null,
          author_ids: form.author_ids,
        }),
      });
      setForm({ title: "", isbn: "", category_id: "", author_ids: [] });
    }, "Đã thêm đầu sách.");
  };

  const addAuthor = (e) => {
    e.preventDefault();
    run(async () => {
      await api("/authors", { method: "POST", headers: JSON_HEADER,
                              body: JSON.stringify({ name: newAuthor }) });
      setNewAuthor("");
    }, "Đã thêm tác giả.");
  };

  const addCategory = (e) => {
    e.preventDefault();
    run(async () => {
      await api("/categories", { method: "POST", headers: JSON_HEADER,
                                 body: JSON.stringify({ name: newCategory }) });
      setNewCategory("");
    }, "Đã thêm chủ đề.");
  };

  const addCopy = (bookId) =>
    run(async () => {
      await api("/copies", {
        method: "POST",
        headers: JSON_HEADER,
        body: JSON.stringify({ book_id: bookId, barcode: barcodes[bookId] || "" }),
      });
      setBarcodes({ ...barcodes, [bookId]: "" });
    }, "Đã thêm bản sách.");

  const uploadCover = (bookId, file) => {
    if (!file) return;
    run(async () => {
      const fd = new FormData();
      fd.append("file", file);
      await api(`/books/${bookId}/cover`, { method: "POST", body: fd });
    }, "Đã upload ảnh bìa.");
  };

  return (
    <div>
      <h2>Quản lý sách</h2>
      {msg && <p className="ok">{msg}</p>}
      {error && <p className="error">{error}</p>}

      <div className="box">
        <b>Thêm tác giả / chủ đề</b>
        <form onSubmit={addAuthor} style={{ marginTop: 8 }}>
          <input placeholder="Tên tác giả" value={newAuthor}
                 onChange={(e) => setNewAuthor(e.target.value)} required />
          <button className="btn" type="submit">Thêm tác giả</button>
        </form>
        <form onSubmit={addCategory} style={{ marginTop: 8 }}>
          <input placeholder="Tên chủ đề" value={newCategory}
                 onChange={(e) => setNewCategory(e.target.value)} required />
          <button className="btn" type="submit">Thêm chủ đề</button>
        </form>
      </div>

      <form className="box" onSubmit={createBook}>
        <b>Thêm đầu sách</b>
        <p>
          <input placeholder="Tên sách" value={form.title}
                 onChange={(e) => setForm({ ...form, title: e.target.value })} required />
          <input placeholder="ISBN" value={form.isbn}
                 onChange={(e) => setForm({ ...form, isbn: e.target.value })} />
        </p>
        <p>
          <select value={form.category_id}
                  onChange={(e) => setForm({ ...form, category_id: e.target.value })}>
            <option value="">-- Chủ đề --</option>
            {categories.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
          </select>
          <select multiple value={form.author_ids.map(String)}
                  onChange={(e) => setForm({
                    ...form,
                    author_ids: Array.from(e.target.selectedOptions, (o) => Number(o.value)),
                  })}>
            {authors.map((a) => <option key={a.id} value={a.id}>{a.name}</option>)}
          </select>
          <small> (giữ Ctrl để chọn nhiều tác giả)</small>
        </p>
        <button className="btn" type="submit">Thêm sách</button>
      </form>

      {books.map((b) => (
        <div className="card" key={b.id}>
          {b.cover_url ? <img src={API + b.cover_url} alt={b.title} /> : <img alt="" />}
          <div className="info">
            <h3 style={{ margin: "0 0 6px" }}>{b.title}</h3>
            <div>Tác giả: {b.authors.map((a) => a.name).join(", ") || "—"}</div>
            <div>Còn lại: <b>{b.available_copies}</b> bản</div>
            <p>
              <input placeholder="Mã vạch, vd CNTT-0003" value={barcodes[b.id] || ""}
                     onChange={(e) => setBarcodes({ ...barcodes, [b.id]: e.target.value })} />
              <button className="btn" onClick={() => addCopy(b.id)}>Thêm bản</button>
            </p>
            <div>
              Ảnh bìa: <input type="file" accept="image/png,image/jpeg,image/webp"
                              onChange={(e) => uploadCover(b.id, e.target.files[0])} />
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}