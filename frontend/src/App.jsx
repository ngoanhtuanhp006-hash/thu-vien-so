import { useEffect, useState } from "react";
import { BrowserRouter, Link, Route, Routes } from "react-router-dom";
import { api, getToken } from "./api";
import Books from "./pages/Books";
import Login from "./pages/Login";
import MyLoans from "./pages/MyLoans";

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

  return (
    <BrowserRouter>
      <nav>
        <b style={{ color: "#fff" }}>Thư viện số Khoa CNTT</b>
        <Link to="/">Tra cứu sách</Link>
        {user && <Link to="/my-loans">Lịch sử mượn</Link>}
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
        </Routes>
      </main>
    </BrowserRouter>
  );
}