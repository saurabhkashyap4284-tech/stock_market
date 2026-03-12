// ── Formatters ────────────────────────────────────────────────
export const fmt    = v => v?.toLocaleString("en-IN") ?? "—";
export const fmtVol = v => {
  if (!v) return "—";
  if (v >= 1e7) return (v / 1e7).toFixed(1) + "Cr";
  if (v >= 1e5) return (v / 1e5).toFixed(1) + "L";
  if (v >= 1e3) return (v / 1e3).toFixed(0) + "K";
  return String(v);
};
export const pDiff  = (a, b) => (a && b) ? +((b - a) / a * 100).toFixed(2) : 0;
export const sign   = v => (v > 0 ? "+" : "") + v + "%";
export const clr    = v => v > 0 ? "#00f5a0" : v < 0 ? "#ff4757" : "#64748b";
export const bg     = v => v > 0 ? "rgba(0,245,160,0.08)" : v < 0 ? "rgba(255,71,87,0.08)" : "rgba(100,116,139,0.06)";

// ── Signal Meta ───────────────────────────────────────────────
export const SIGNAL_META = {
  BEARISH:          { color: "#ff4757", bg: "rgba(255,71,87,0.1)",   border: "rgba(255,71,87,0.3)",   icon: "🔴", label: "BEARISH" },
  BEARISH_TRAP:     { color: "#ff6b35", bg: "rgba(255,107,53,0.1)",  border: "rgba(255,107,53,0.3)",  icon: "🪤", label: "BEARISH TRAP" },
  BEARISH_ZONE:     { color: "#ffa500", bg: "rgba(255,165,0,0.08)",  border: "rgba(255,165,0,0.25)",  icon: "⚠️", label: "BEARISH ZONE" },
  BULLISH:          { color: "#00f5a0", bg: "rgba(0,245,160,0.1)",   border: "rgba(0,245,160,0.3)",   icon: "🟢", label: "BULLISH" },
  BULLISH_PULLBACK: { color: "#00c9a7", bg: "rgba(0,201,167,0.1)",   border: "rgba(0,201,167,0.3)",   icon: "🎯", label: "BULL PULLBACK" },
  BULLISH_ZONE:     { color: "#ffd700", bg: "rgba(255,215,0,0.08)",  border: "rgba(255,215,0,0.25)",  icon: "👀", label: "BULLISH ZONE" },
  NEUTRAL:          { color: "#475569", bg: "rgba(71,85,105,0.06)",  border: "rgba(71,85,105,0.2)",   icon: "⚪", label: "NEUTRAL" },
};

export const PHASE_META = {
  PRE:    { label: "⏳ Pre-Market",           color: "#64748b", desc: "Market 9:15 AM pe khulay ga" },
  CANDLE: { label: "🕯️ 5-Min Candle Build",  color: "#ffd700", desc: "9:15→9:20 | OHLC capture ho raha hai" },
  WATCH:  { label: "🎯 Signal Window",        color: "#ff9f43", desc: "9:20→9:30 | Live signals active" },
  OPEN:   { label: "📈 Market Open",          color: "#00f5a0", desc: "Full trading session" },
  CLOSED: { label: "🔒 Market Closed",        color: "#334155", desc: "Kal milte hain!" },
};

export const TABS = [
  { key: "ALL",          label: "📋 All",           color: "#64748b" },
  { key: "BEARISH",      label: "🔴 Bearish",        color: "#ff4757" },
  { key: "BEARISH_ZONE", label: "⚠️ Bearish Zone",  color: "#ffa500" },
  { key: "BULLISH",      label: "🟢 Bullish",        color: "#00f5a0" },
  { key: "BULLISH_ZONE", label: "👀 Bullish Zone",   color: "#ffd700" },
];

export const INDICES = new Set(["NIFTY","BANKNIFTY","FINNIFTY","MIDCPNIFTY","NIFTYNXT50"]);
