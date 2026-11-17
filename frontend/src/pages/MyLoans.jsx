import { useEffect, useState } from "react";
import { api } from "../api";

function fmt(d) {
  return d ? new Date(d).toLocaleDateString("vi-VN") : "—";
}

const STATUS = {
  requested: "Chờ nhận sách",
  borrowed: "Đang mượn",
  returned: "Đã trả",
  cancelled: "Đã hủy",
};

export default function MyLoans() {
  const [loans, setLoans] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    api("/me/loans").then(setLoans).catch((e) => setError(e.message));
  }, []);

  return (
    <div>
      <h2>Lịch sử mượn của tôi</h2>
      {error && <p className="error">{error}</p>}
      <table>
        <thead>
          <tr>
            <th>Sách</th><th>Trạng thái</th><th>Ngày mượn</th>
            <th>Hạn trả</th><th>Ngày trả</th><th>Quá hạn</th><th>Tiền phạt</th>
          </tr>
        </thead>
        <tbody>
          {loans.map((l) => (
            <tr key={l.id}>
              <td>{l.book_title}</td>
              <td>{STATUS[l.status] || l.status}</td>
              <td>{fmt(l.borrowed_at)}</td>
              <td>{fmt(l.due_date)}</td>
              <td>{fmt(l.returned_at)}</td>
              <td>{l.overdue_days} ngày</td>
              <td>{l.fine_amount.toLocaleString("vi-VN")} đ</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}