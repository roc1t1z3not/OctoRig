import axios from "axios";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "";

export const apiClient = axios.create({
  baseURL: `${API_BASE}/api/v1`,
  headers: { "Content-Type": "application/json" },
});

// Attach JWT on every request
apiClient.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    try {
      const raw = localStorage.getItem("octorig_user");
      const token = raw ? JSON.parse(raw).state?.accessToken : null;
      if (token) config.headers.Authorization = `Bearer ${token}`;
    } catch {
      // ignore parse errors
    }
  }
  return config;
});

// Redirect to login on 401 — but never when already on /login (prevents reload loop)
apiClient.interceptors.response.use(
  (r) => r,
  (err) => {
    if (
      err.response?.status === 401 &&
      typeof window !== "undefined" &&
      !window.location.pathname.startsWith("/login")
    ) {
      window.location.href = "/login";
    }
    return Promise.reject(err);
  }
);
