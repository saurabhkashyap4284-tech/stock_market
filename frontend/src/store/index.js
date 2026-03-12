import { create } from "zustand";

// ── Auth Store ────────────────────────────────────────────────
export const useAuthStore = create((set) => ({
  user:      null,
  isLoggedIn: !!localStorage.getItem("access_token"),

  login: (accessToken, refreshToken, user) => {
    localStorage.setItem("access_token",  accessToken);
    localStorage.setItem("refresh_token", refreshToken);
    set({ user, isLoggedIn: true });
  },

  logout: () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    set({ user: null, isLoggedIn: false });
  },

  setUser: (user) => set({ user }),
}));


// ── Market Store ──────────────────────────────────────────────
export const useMarketStore = create((set, get) => ({
  stocks:      {},        // symbol → stock data
  signals:     {},        // symbol → signal
  candles:     {},        // symbol → 5min candle
  phase:       "PRE",
  lastTick:    null,
  wsConnected: false,
  activeTab:   "ALL",
  search:      "",

  // Called on every WS tick
  updateFromWS: (payload) => {
    const { phase, stocks, tick_at } = payload;
    const stockMap  = {};
    const signalMap = {};
    const candleMap = {};

    stocks.forEach(s => {
      stockMap[s.symbol]  = s;
      signalMap[s.symbol] = s.signal;
      candleMap[s.symbol] = s.candle;
    });

    set(state => ({
      stocks:   { ...state.stocks,  ...stockMap  },
      signals:  { ...state.signals, ...signalMap },
      candles:  { ...state.candles, ...candleMap },
      phase,
      lastTick: tick_at,
    }));
  },

  setInitialState: (payload) => {
    const stockMap = {}, signalMap = {}, candleMap = {};
    payload.stocks.forEach(s => {
      stockMap[s.symbol]  = s;
      signalMap[s.symbol] = s.signal;
      candleMap[s.symbol] = s.candle;
    });
    set({ stocks: stockMap, signals: signalMap, candles: candleMap, phase: payload.phase });
  },

  setWsConnected: (v) => set({ wsConnected: v }),
  setActiveTab:   (v) => set({ activeTab: v, search: "" }),
  setSearch:      (v) => set({ search: v }),

  // Derived — all stocks as array
  getStockList: () => Object.values(get().stocks),

  // Counts per signal bucket
  getCounts: () => {
    const sigs = get().signals;
    return {
      BEARISH:         Object.values(sigs).filter(s => ["BEARISH","BEARISH_TRAP"].includes(s?.signal)).length,
      BEARISH_ZONE:    Object.values(sigs).filter(s => s?.signal === "BEARISH_ZONE").length,
      BULLISH:         Object.values(sigs).filter(s => ["BULLISH","BULLISH_PULLBACK"].includes(s?.signal)).length,
      BULLISH_ZONE:    Object.values(sigs).filter(s => s?.signal === "BULLISH_ZONE").length,
    };
  },
}));


// ── Alerts Store ──────────────────────────────────────────────
export const useAlertsStore = create((set) => ({
  toasts: [],   // corner notifications

  addToast: (toast) =>
    set(state => ({ toasts: [{ ...toast, id: Date.now() + toast.symbol }, ...state.toasts].slice(0, 6) })),

  removeToast: (id) =>
    set(state => ({ toasts: state.toasts.filter(t => t.id !== id) })),
}));
