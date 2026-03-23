import { useMemo } from "react";
import { useMarketStore } from "../../store";
import { TABS, fmt, clr, pDiff } from "../../utils";
import SignalBadge from "./SignalBadge";

export default function StockTable() {
  const { stocks, signals, activeTab, search, setActiveTab, setSearch } = useMarketStore();

  const filtered = useMemo(() => {
    let list = Object.entries(stocks).map(([sym, data]) => ({ symbol: sym, ...data, signal: signals[sym] }));
    
    if (activeTab !== "ALL") {
      list = list.filter(s => {
        const sig = s.signal || { signal: "NEUTRAL" };
        if (activeTab === "FALSE_ALERTS") return sig.signal === "FALSE_ALERT_BULL" || sig.signal === "FALSE_ALERT_BEAR";
        if (activeTab === "BULLISH")      return sig.signal === "BULLISH";
        if (activeTab === "BEARISH")      return sig.signal === "BEARISH";
        return sig.signal === activeTab;
      });
    }
    
    if (search) {
      list = list.filter(s => s.symbol.includes(search.toUpperCase()));
    }
    
    return list;
  }, [stocks, signals, activeTab, search]);

  return (
    <div style={{ padding: "20px" }}>
      {/* Tabs */}
      <div style={{ display: "flex", gap: "10px", marginBottom: "15px", overflowX: "auto" }}>
        {TABS.map(tab => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key)}
            style={{
              padding: "8px 14px",
              borderRadius: "4px",
              border: activeTab === tab.key ? `2px solid ${tab.color}` : "1px solid #475569",
              backgroundColor: activeTab === tab.key ? tab.color + "20" : "transparent",
              color: activeTab === tab.key ? tab.color : "#94a3b8",
              cursor: "pointer",
              fontSize: "13px",
              fontWeight: activeTab === tab.key ? "bold" : "normal",
            }}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Search */}
      <div style={{ marginBottom: "15px" }}>
        <input
          type="text"
          placeholder="Search symbol..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          style={{ padding: "8px 12px", width: "200px", borderRadius: "4px", border: "1px solid #475569", backgroundColor: "#1e293b", color: "white" }}
        />
      </div>

      {/* Table */}
      <table style={{ width: "100%", borderCollapse: "collapse" }}>
        <thead>
          <tr style={{ borderBottom: "1px solid #334155" }}>
            <th style={{ padding: "10px", textAlign: "left", color: "#94a3b8" }}>Symbol</th>
            <th style={{ padding: "10px", textAlign: "right", color: "#94a3b8" }}>LTP</th>
            <th style={{ padding: "10px", textAlign: "right", color: "#94a3b8" }}>Baseline</th>
            <th style={{ padding: "10px", textAlign: "right", color: "#94a3b8" }}>Change %</th>
            <th style={{ padding: "10px", textAlign: "right", color: "#94a3b8" }}>Volume</th>
            <th style={{ padding: "10px", textAlign: "center", color: "#94a3b8" }}>Signal</th>
            <th style={{ padding: "10px", textAlign: "left", color: "#94a3b8" }}>Time</th>
          </tr>
        </thead>
        <tbody>
          {filtered.map(stock => {
            const change = stock.prev_close ? pDiff(stock.prev_close, stock.ltp) : 0;
            const signalTs = stock.signal?.signal_ts;
            return (
              <tr key={stock.symbol} style={{ borderBottom: "1px solid #334155", height: "45px" }}>
                <td style={{ padding: "10px", fontWeight: "bold", color: "#f8fafc" }}>{stock.symbol}</td>
                <td style={{ padding: "10px", textAlign: "right", color: clr(change) }}>₹{fmt(stock.ltp)}</td>
                <td style={{ padding: "10px", textAlign: "right", color: "#64748b" }}>
                  {stock.baseline_ltp ? `₹${fmt(stock.baseline_ltp)}` : "—"}
                </td>
                <td style={{ padding: "10px", textAlign: "right", color: clr(change), fontWeight: "bold" }}>
                  {change > 0 ? "+" : ""}{change.toFixed(2)}%
                </td>
                <td style={{ padding: "10px", textAlign: "right", color: "#94a3b8" }}>{fmt(stock.volume)}</td>
                <td style={{ padding: "10px", textAlign: "center" }}>
                  <SignalBadge signal={stock.signal?.signal} />
                </td>
                <td style={{ padding: "10px", color: "#94a3b8", fontSize: "12px" }}>
                  {signalTs ? new Date(signalTs).toLocaleTimeString("en-IN") : "—"}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>

      {filtered.length === 0 && <div style={{ padding: "20px", textAlign: "center", color: "#94a3b8" }}>No stocks found</div>}
    </div>
  );
}
