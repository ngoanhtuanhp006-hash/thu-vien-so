import { useEffect, useState } from "react";
import { api, API } from "../api";

export default function Books({ user }) {
  const [q, setQ] = useState("");
  const [data, setData] = useState({ items: [], total: 0 });
  const [page, setPage] = useState(1);
  const [msg, setMsg] = useState("");
  const [error, setError] = useState("");

  async function load(p = page) {
    try {
      const res = await api(`/books?q=${encodeURIComponent(q)}&page=${p}&size=5`);
      setData(res);
    } catch (err) {
      setError(err.message);
    }
  }

  useEffect(() => {
    load(page);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [page]);

  function search(e) {
    e.preventDefault();
    setPage(1);
    load(1);
  }

  async function borrow(bookId) {
    setMsg("");
    setError("");
    try {
      await api("/loans", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ book_id: bookId }),
      });
      setMsg("Đặt mượn thành công, hãy đến thư viện nhận sách.");
      load();
    } catch (err) {
      setError(err.message);
    }
  }

  const totalPages = Math.max(1, Math.ceil(data.total / 5));

  return (
    <div>
      <h2>Tra cứu sách</h2>
      <form onSubmit={search}>
        <input placeholder="Nhập tên sách..." value={q}
               onChange={(e) => setQ(e.target.value)} />
        <button className="btn" type="submit">Tìm</button>
      </form>
      {msg && <p className="ok">{msg}</p>}
      {error && <p className="error">{error}</p>}
      <p>Tìm thấy {data.total} cuốn</p>

      {data.items.map((b) => (
        <div className="card" key={b.id}>
          {b.cover_url ? <img src={API + b.cover_url} alt={b.title} /> : <img alt="" />}
          <div className="info">
            <h3 style={{ margin: "0 0 6px" }}>{b.title}</h3>
            <div>Tác giả: {b.authors.map((a) => a.name).join(", ") || "—"}</div>
            <div>Chủ đề: {b.category ? b.category.name : "—"}</div>
            <div>Còn lại: <b>{b.available_copies}</b> bản</div>
          </div>
          {user && (
            <button className="btn" disabled={b.available_copies === 0}
                    onClick={() => borrow(b.id)}>
              Đặt mượn
            </button>
          )}
        </div>
      ))}

      <button className="btn" disabled={page <= 1} onClick={() => setPage(page - 1)}>Trước</button>{" "}
      Trang {page}/{totalPages}{" "}
      <button className="btn" disabled={page >= totalPages} onClick={() => setPage(page + 1)}>Sau</button>
    </div>
  );
}