import { useEffect, useState } from "react";
import { api } from "../api";

function fmt(d) {
  return d ? new Date(d).toLocaleDateString("vi-VN") : "—";
}

const STATUS = {
  requested: "Chờ giao sách",
  borrowed: "Đang mượn",
  returned: "Đã trả",
};

export default function LibrarianLoans() {
  const [status, setStatus] = useState("requested");
  const [loans, setLoans] = useState([]);
  const [msg, setMsg] = useState("");
  const [error, setError] = useState("");

  async function load() {
    try {
      const q = status ? `?status=${status}` : "";
      setLoans(await api("/loans" + q));
    } catch (e) {
      setError(e.message);
    }
  }

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [status]);

  async function act(id, action) {
    setMsg("");
    setError("");
    try {
      await api(`/loans/${id}/${action}`, { method: "POST" });
      setMsg(action === "checkout" ? "Đã giao sách." : "Đã nhận trả sách.");
      load();
    } catch (e) {
      setError(e.message);
    }
  }

  return (
    <div>
      <h2>Giao / nhận sách</h2>
      <div className="tabs">
        {Object.entries(STATUS).map(([k, v]) => (
          <button key={k} className={status === k ? "active" : ""}
                  onClick={() => setStatus(k)}>
            {v}
          </button>
        ))}
        <button className={status === "" ? "active" : ""}
                onClick={() => setStatus("")}>
          Tất cả
        </button>
      </div>
      {msg && <p className="ok">{msg}</p>}
      {error && <p className="error">{error}</p>}
      <table>
        <thead>
          <tr>
            <th>#</th><th>Bạn đọc (id)</th><th>Sách</th><th>Mã vạch</th>
            <th>Trạng thái</th><th>Hạn trả</th><th>Quá hạn</th>
            <th>Tiền phạt</th><th></th>
          </tr>
        </thead>
        <tbody>
          {loans.map((l) => (
            <tr key={l.id}>
              <td>{l.id}</td>
              <td>{l.user_id}</td>
              <td>{l.book_title}</td>
              <td>{l.barcode}</td>
              <td>{STATUS[l.status] || l.status}</td>
              <td>{fmt(l.due_date)}</td>
              <td>{l.overdue_days} ngày</td>
              <td>{l.fine_amount.toLocaleString("vi-VN")} đ</td>
              <td>
                {l.status === "requested" && (
                  <button className="btn" onClick={() => act(l.id, "checkout")}>Giao sách</button>
                )}
                {l.status === "borrowed" && (
                  <button className="btn" onClick={() => act(l.id, "return")}>Nhận trả</button>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}