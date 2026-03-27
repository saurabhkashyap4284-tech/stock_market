import axios from "axios";

// ── Dynamic API URL Logic ──────────────────────────────────────
const getApiUrl = () => {
  const envUrl = import.meta.env.VITE_API_URL;
  if (!envUrl) return "http://localhost:8000";
  // If envUrl is just a hostname (no protocol), prepend https or current protocol
  if (!envUrl.startsWith("http")) {
    const protocol = window.location.protocol === "https:" ? "https" : "http";
    return `${protocol}://${envUrl}`;
  }
  return envUrl;
};

const BASE_URL = getApiUrl();

const api = axios.create({
  baseURL: BASE_URL,
  headers: { "Content-Type": "application/json" },
});

// ── Request interceptor — JWT token lagao ─────────────────────
api.interceptors.request.use(config => {
  const token = localStorage.getItem("access_token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// ── Response interceptor — token refresh ──────────────────────
api.interceptors.response.use(
  res => res,
  async err => {
    const original = err.config;
    if (err.response?.status === 401 && !original._retry) {
      original._retry = true;
      try {
        const refresh = localStorage.getItem("refresh_token");
        const res = await axios.post(`${BASE_URL}/api/auth/refresh/`, { refresh });
        localStorage.setItem("access_token", res.data.access);
        original.headers.Authorization = `Bearer ${res.data.access}`;
        return api(original);
      } catch {
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        window.location.href = "/login";
      }
    }
    return Promise.reject(err);
  }
);

// ── Auth endpoints ────────────────────────────────────────────
export const authAPI = {
  login:    (data) => api.post("/api/auth/login/",       data),
  refresh:  (data) => api.post("/api/auth/refresh/",     data),
  register: (data) => api.post("/api/users/register/",   data),
};

// ── Market endpoints ──────────────────────────────────────────
export const marketAPI = {
  liveSnapshot: (params) => api.get("/api/market/live/",        { params }),
  liveStock:    (symbol) => api.get(`/api/market/live/${symbol}/`),
  stocks:       ()       => api.get("/api/market/stocks/"),
  candles:      (params) => api.get("/api/market/candles/",     { params }),
  oiHistory:    (params) => api.get("/api/market/oi-history/",  { params }),
  phase:        ()       => api.get("/api/market/phase/"),
  signalLogs:   (params) => api.get("/api/market/signal-logs/", { params }),
  downloadSignalLogs: (params) => api.get("/api/market/signal-logs/download/", { params, responseType: "blob" }),
  purgeData:    (days=0)  => api.post("/api/market/purge/", { days }),
  clearState:   ()       => api.post("/api/market/clear-state/"),
};

// ── Signals endpoints ─────────────────────────────────────────
export const signalsAPI = {
  history:  (params)     => api.get("/api/signals/history/",           { params }),
  summary:  (params)     => api.get("/api/signals/summary/",           { params }),
  timeline: (sym,params) => api.get(`/api/signals/timeline/${sym}/`,   { params }),
};

// ── Alert endpoints ───────────────────────────────────────────
export const alertsAPI = {
  getRules:    ()       => api.get("/api/alerts/rules/"),
  createRule:  (data)   => api.post("/api/alerts/rules/",      data),
  updateRule:  (id,d)   => api.put(`/api/alerts/rules/${id}/`, d),
  deleteRule:  (id)     => api.delete(`/api/alerts/rules/${id}/`),
  toggleRule:  (id)     => api.post(`/api/alerts/rules/${id}/toggle/`),
  getLogs:     ()       => api.get("/api/alerts/logs/"),
};

// ── User endpoints ────────────────────────────────────────────
export const usersAPI = {
  profile:          ()       => api.get("/api/users/profile/"),
  updateProfile:    (data)   => api.put("/api/users/profile/", data),
  getWatchlists:    ()       => api.get("/api/users/watchlists/"),
  createWatchlist:  (data)   => api.post("/api/users/watchlists/",      data),
  updateWatchlist:  (id,d)   => api.put(`/api/users/watchlists/${id}/`, d),
  deleteWatchlist:  (id)     => api.delete(`/api/users/watchlists/${id}/`),
  addSymbol:        (id,sym) => api.post(`/api/users/watchlists/${id}/add/`,    { symbol: sym }),
  removeSymbol:     (id,sym) => api.post(`/api/users/watchlists/${id}/remove/`, { symbol: sym }),
};

export default api;
