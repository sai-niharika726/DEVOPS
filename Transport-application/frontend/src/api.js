const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:5000";

function authHeaders() {
  const token = localStorage.getItem("token");
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function request(path, options = {}) {
  const res = await fetch(`${BASE_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...authHeaders(),
      ...(options.headers || {}),
    },
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    throw new Error(data.error || "Something went wrong. Try again.");
  }
  return data;
}

export const api = {
  signup: (payload) =>
    request("/api/signup", { method: "POST", body: JSON.stringify(payload) }),
  login: (payload) =>
    request("/api/login", { method: "POST", body: JSON.stringify(payload) }),
  me: () => request("/api/me"),
  quote: (payload) =>
    request("/api/pass/quote", { method: "POST", body: JSON.stringify(payload) }),
  applyPass: (payload) =>
    request("/api/pass/apply", { method: "POST", body: JSON.stringify(payload) }),
  confirmPass: (id, payload) =>
    request(`/api/pass/${id}/confirm`, { method: "POST", body: JSON.stringify(payload) }),
  myPasses: () => request("/api/pass/my"),
};
