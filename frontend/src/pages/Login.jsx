import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api";

export default function Login({ onLogin }) {
  const [isRegister, setIsRegister] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  async function submit(e) {
    e.preventDefault();
    setError("");
    try {
      if (isRegister) {
        await api("/auth/register", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email, password, full_name: fullName }),
        });
      }
      const data = await api("/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: new URLSearchParams({ username: email, password }),
      });
      localStorage.setItem("token", data.access_token);
      await onLogin();
      navigate("/");
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <form onSubmit={submit}>
      <h2>{isRegister ? "Đăng ký" : "Đăng nhập"}</h2>
      {isRegister && (
        <p>
          <input placeholder="Họ tên" value={fullName}
                 onChange={(e) => setFullName(e.target.value)} required />
        </p>
      )}
      <p>
        <input type="email" placeholder="Email" value={email}
               onChange={(e) => setEmail(e.target.value)} required />
      </p>
      <p>
        <input type="password" placeholder="Mật khẩu" value={password}
               onChange={(e) => setPassword(e.target.value)} required />
      </p>
      <button className="btn" type="submit">
        {isRegister ? "Đăng ký" : "Đăng nhập"}
      </button>{" "}
      <button type="button" onClick={() => setIsRegister(!isRegister)}>
        {isRegister ? "Đã có tài khoản?" : "Chưa có tài khoản?"}
      </button>
      {error && <p className="error">{error}</p>}
    </form>
  );
}