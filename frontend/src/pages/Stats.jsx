import { useEffect, useState } from "react";
import { api } from "../api";

export default function Stats() {
  const [rows, setRows] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    api("/stats/top-books?limit=10").then(setRows).catch((e) => setError(e.message));
  }, []);

  return (
    <div>
      <h2>Sách được mượn nhiều nhất</h2>
      {error && <p className="error">{error}</p>}
      <table>
        <thead>
          <tr><th>Hạng</th><th>Sách</th><th>Số lượt mượn</th></tr>
        </thead>
        <tbody>
          {rows.map((r, i) => (
            <tr key={r.book_id}>
              <td>{i + 1}</td><td>{r.title}</td><td>{r.borrow_count}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}