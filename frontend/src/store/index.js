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
  selectedKPI: null,       // which KPI card is clicked for drilldown
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
  setActiveTab:   (v) => set({ activeTab: v, search: "", selectedKPI: null }),
  setSelectedKPI: (v) => set({ selectedKPI: v }),
  setSearch:      (v) => set({ search: v }),

  // Derived — all stocks as array
  getStockList: () => Object.values(get().stocks),

  // Counts per signal bucket
  getCounts: () => {
    const sigs = Object.values(get().signals).map(s => s?.signal || "NEUTRAL");

    const counts = {
      BEARISH:          sigs.filter(s => s === "BEARISH_FALL").length,
      BULLISH:          sigs.filter(s => s === "BULLISH_BREAKOUT").length,
      FALSE_ALERT_BULL: sigs.filter(s => s === "BULLISH_FAILED").length,
      FALSE_ALERT_BEAR: sigs.filter(s => s === "BEARISH_FAILED").length,
    };

    // Derived statistics
    counts.FALSE_ALERTS = counts.FALSE_ALERT_BULL + counts.FALSE_ALERT_BEAR;

    // Accuracy Calculation
    // Accuracy % = (Active) / (Active + Failed) * 100
    const bullTotal = counts.BULLISH + counts.FALSE_ALERT_BULL;
    const bearTotal = counts.BEARISH + counts.FALSE_ALERT_BEAR;

    counts.BULLISH_ACCURACY = bullTotal > 0 ? Math.round((counts.BULLISH / bullTotal) * 100) : 0;
    counts.BEARISH_ACCURACY = bearTotal > 0 ? Math.round((counts.BEARISH / bearTotal) * 100) : 0;

    return counts;
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
