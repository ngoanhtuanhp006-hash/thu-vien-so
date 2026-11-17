import { useEffect, useState } from "react";
import { BrowserRouter, Link, Route, Routes } from "react-router-dom";
import { api, getToken } from "./api";
import Books from "./pages/Books";
import Login from "./pages/Login";
import MyLoans from "./pages/MyLoans";
import LibrarianLoans from "./pages/LibrarianLoans";
import LibrarianBooks from "./pages/LibrarianBooks";
import Stats from "./pages/Stats";

export default function App() {
  const [user, setUser] = useState(null);

  async function loadUser() {
    if (!getToken()) {
      setUser(null);
      return;
    }
    try {
      setUser(await api("/me"));
    } catch {
      localStorage.removeItem("token");
      setUser(null);
    }
  }

  useEffect(() => {
    loadUser();
  }, []);

  function logout() {
    localStorage.removeItem("token");
    setUser(null);
  }

  const isLibrarian = user && user.role === "librarian";

  return (
    <BrowserRouter>
      <nav>
        <b style={{ color: "#fff" }}>Thư viện số Khoa CNTT</b>
        <Link to="/">Tra cứu sách</Link>
        {user && !isLibrarian && <Link to="/my-loans">Lịch sử mượn</Link>}
        {isLibrarian && (
          <>
            <Link to="/lib/loans">Giao / nhận sách</Link>
            <Link to="/lib/books">Quản lý sách</Link>
            <Link to="/lib/stats">Thống kê</Link>
          </>
        )}
        <span className="spacer" />
        {user ? (
          <>
            <span style={{ color: "#fff" }}>{user.full_name}</span>
            <button onClick={logout}>Đăng xuất</button>
          </>
        ) : (
          <Link to="/login">Đăng nhập</Link>
        )}
      </nav>
      <main>
        <Routes>
          <Route path="/" element={<Books user={user} />} />
          <Route path="/login" element={<Login onLogin={loadUser} />} />
          <Route path="/my-loans" element={<MyLoans />} />
          <Route path="/lib/loans" element={isLibrarian ? <LibrarianLoans /> : <p>Chỉ dành cho thủ thư.</p>} />
          <Route path="/lib/books" element={isLibrarian ? <LibrarianBooks /> : <p>Chỉ dành cho thủ thư.</p>} />
          <Route path="/lib/stats" element={isLibrarian ? <Stats /> : <p>Chỉ dành cho thủ thư.</p>} />
        </Routes>
      </main>
    </BrowserRouter>
  );
}