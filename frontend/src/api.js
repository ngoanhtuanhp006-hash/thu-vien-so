export const API = "http://127.0.0.1:8000";

export function getToken() {
  return localStorage.getItem("token");
}

export async function api(path, options = {}) {
  const headers = { ...(options.headers || {}) };
  const token = getToken();
  if (token) headers.Authorization = `Bearer ${token}`;
  const res = await fetch(API + path, { ...options, headers });
  if (!res.ok) {
    let msg = "Lỗi " + res.status;
    try {
      const d = await res.json();
      if (typeof d.detail === "string") msg = d.detail;
    } catch {
      /* bo qua */
    }
    throw new Error(msg);
  }
  return res.status === 204 ? null : res.json();
}