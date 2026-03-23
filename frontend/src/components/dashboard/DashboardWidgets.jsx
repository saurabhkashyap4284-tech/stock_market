import { useMarketStore } from "../../store";
import { PHASE_META, SIGNAL_META } from "../../utils";
import { marketAPI } from "../../api";
import { useState, useEffect } from "react";

export default function DashboardWidgets() {
  const { phase, getCounts, selectedKPI, setSelectedKPI } = useMarketStore();
  const counts = getCounts();
  const phaseMeta = PHASE_META[phase] || PHASE_META.PRE;

  const [drilldownData, setDrilldownData] = useState([]);
  const [loadingDrilldown, setLoadingDrilldown] = useState(false);
  const [isPurging, setIsPurging] = useState(false);

  const cards = [
    { key: "BEARISH",       count: counts.BEARISH,       meta: SIGNAL_META.BEARISH },
    { key: "BULLISH",       count: counts.BULLISH,       meta: SIGNAL_META.BULLISH },
    { key: "FALSE_ALERTS",  count: counts.FALSE_ALERTS,  meta: { color: "#fb7185", bg: "rgba(251,113,133,0.08)", border: "rgba(251,113,133,0.3)", icon: "❌", label: "FALSE ALERTS" } },
  ];

  // Fetch drilldown data when a KPI is selected
  useEffect(() => {
    if (!selectedKPI) {
      setDrilldownData([]);
      return;
    }
    setLoadingDrilldown(true);
    marketAPI.signalLogs({ type: selectedKPI })
      .then(res => setDrilldownData(res.data))
      .catch(err => console.error("Drilldown fetch error:", err))
      .finally(() => setLoadingDrilldown(false));
  }, [selectedKPI]);

  const handleCardClick = (key) => {
    setSelectedKPI(selectedKPI === key ? null : key);
  };

  const handleCleanData = async () => {
    if (!window.confirm("Are you sure you want to clean all historical snapshots from the database?")) return;
    setIsPurging(true);
    try {
      const res = await marketAPI.purgeData(0);
      alert(res.data.message);
    } catch (err) {
      alert("Failed to clean data: " + (err.response?.data?.error || err.message));
    } finally {
      setIsPurging(false);
    }
  };

  const handleResetMarket = async () => {
    if (!window.confirm("Reset Live Market State? This will clear all current signals and candles from Redis.")) return;
    setIsPurging(true);
    try {
      const res = await marketAPI.clearState();
      alert(res.data.message);
      window.location.reload();
    } catch (err) {
      alert("Failed to reset market: " + (err.response?.data?.error || err.message));
    } finally {
      setIsPurging(false);
    }
  };

  return (
    <div style={{ padding: "20px" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "20px", gap: "10px" }}>
        <h2 style={{ margin: 0, color: "#f8fafc" }}>Market Dashboard</h2>
        <div style={{ display: "flex", gap: "10px" }}>
          <button
            onClick={handleResetMarket}
            disabled={isPurging}
            style={{
              padding: "8px 16px",
              backgroundColor: "#f59e0b",
              color: "white",
              border: "none",
              borderRadius: "6px",
              cursor: isPurging ? "not-allowed" : "pointer",
              fontWeight: "bold",
              opacity: isPurging ? 0.7 : 1,
            }}
          >
            🔄 Reset Live Data
          </button>
          <button
            onClick={handleCleanData}
            disabled={isPurging}
            style={{
              padding: "8px 16px",
              backgroundColor: "#ef4444",
              color: "white",
              border: "none",
              borderRadius: "6px",
              cursor: isPurging ? "not-allowed" : "pointer",
              fontWeight: "bold",
              opacity: isPurging ? 0.7 : 1,
            }}
          >
            {isPurging ? "Cleaning..." : "🗑️ Clean DB"}
          </button>
        </div>
      </div>

      {/* Phase Banner */}
      <div
        style={{
          padding: "20px",
          borderRadius: "8px",
          backgroundColor: phaseMeta.color + "15",
          border: `2px solid ${phaseMeta.color}`,
          marginBottom: "20px",
        }}
      >
        <div style={{ fontSize: "20px", fontWeight: "bold", marginBottom: "5px" }}>{phaseMeta.label}</div>
        <div style={{ color: "#94a3b8", fontSize: "14px" }}>{phaseMeta.desc}</div>
      </div>

      {/* KPI Signal Cards — Clickable */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "15px" }}>
        {cards.map(card => (
          <div
            key={card.key}
            onClick={() => handleCardClick(card.key)}
            style={{
              padding: "20px",
              borderRadius: "8px",
              backgroundColor: selectedKPI === card.key ? card.meta.bg.replace("0.08", "0.25").replace("0.1", "0.25") : card.meta.bg,
              border: `2px solid ${selectedKPI === card.key ? card.meta.color : (card.meta.border || card.meta.color + "50")}`,
              textAlign: "center",
              cursor: "pointer",
              transition: "all 0.2s ease",
              transform: selectedKPI === card.key ? "scale(1.02)" : "scale(1)",
              boxShadow: selectedKPI === card.key ? `0 4px 20px ${card.meta.color}30` : "none",
            }}
          >
            <div style={{ fontSize: "32px", marginBottom: "10px" }}>{card.meta.icon}</div>
            <div style={{ fontSize: "24px", fontWeight: "bold", color: card.meta.color }}>{card.count}</div>
            <div style={{ fontSize: "12px", color: "#94a3b8" }}>{card.meta.label}</div>
            <div style={{ fontSize: "10px", color: "#64748b", marginTop: "5px" }}>
              {selectedKPI === card.key ? "▲ Click to close" : "Click to view stocks"}
            </div>
          </div>
        ))}
      </div>

      {/* Drilldown Panel — Shows when a KPI card is selected */}
      {selectedKPI && (
        <div style={{
          marginTop: "20px",
          padding: "20px",
          borderRadius: "8px",
          backgroundColor: "#1e293b",
          border: "1px solid #334155",
        }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "15px" }}>
            <h3 style={{ margin: 0, color: "#f8fafc" }}>
              {selectedKPI === "FALSE_ALERTS" ? "❌ False Alerts" : SIGNAL_META[selectedKPI]?.icon + " " + SIGNAL_META[selectedKPI]?.label} — Detail
            </h3>
            <button
              onClick={() => setSelectedKPI(null)}
              style={{
                padding: "4px 12px",
                backgroundColor: "#475569",
                color: "white",
                border: "none",
                borderRadius: "4px",
                cursor: "pointer",
                fontSize: "12px",
              }}
            >
              ✕ Close
            </button>
          </div>

          {loadingDrilldown ? (
            <p style={{ color: "#94a3b8" }}>Loading signal logs...</p>
          ) : drilldownData.length === 0 ? (
            <p style={{ color: "#64748b" }}>No signal logs found for today.</p>
          ) : (
            <div style={{ maxHeight: "400px", overflowY: "auto" }}>
              <table style={{ width: "100%", borderCollapse: "collapse" }}>
                <thead>
                  <tr style={{ borderBottom: "2px solid #475569", position: "sticky", top: 0, backgroundColor: "#1e293b" }}>
                    <th style={{ padding: "10px", textAlign: "left", color: "#94a3b8", fontSize: "12px" }}>Symbol</th>
                    <th style={{ padding: "10px", textAlign: "left", color: "#94a3b8", fontSize: "12px" }}>Signal</th>
                    <th style={{ padding: "10px", textAlign: "left", color: "#94a3b8", fontSize: "12px" }}>Time</th>
                    <th style={{ padding: "10px", textAlign: "right", color: "#94a3b8", fontSize: "12px" }}>LTP</th>
                    <th style={{ padding: "10px", textAlign: "right", color: "#94a3b8", fontSize: "12px" }}>Baseline</th>
                    <th style={{ padding: "10px", textAlign: "right", color: "#94a3b8", fontSize: "12px" }}>OI</th>
                    <th style={{ padding: "10px", textAlign: "left", color: "#94a3b8", fontSize: "12px" }}>Reason</th>
                  </tr>
                </thead>
                <tbody>
                  {drilldownData.map((log, idx) => {
                    const sigMeta = SIGNAL_META[log.signal_type] || SIGNAL_META.NEUTRAL;
                    return (
                      <tr key={log.id || idx} style={{ borderBottom: "1px solid #334155" }}>
                        <td style={{ padding: "10px", fontWeight: "bold", color: "#f8fafc" }}>{log.symbol}</td>
                        <td style={{ padding: "10px" }}>
                          <span style={{
                            padding: "3px 8px",
                            borderRadius: "4px",
                            backgroundColor: sigMeta.bg,
                            color: sigMeta.color,
                            fontSize: "11px",
                            fontWeight: "bold",
                          }}>
                            {sigMeta.icon} {log.signal_type}
                          </span>
                        </td>
                        <td style={{ padding: "10px", color: "#94a3b8", fontSize: "13px" }}>
                          {new Date(log.timestamp).toLocaleTimeString("en-IN")}
                        </td>
                        <td style={{ padding: "10px", textAlign: "right", color: "#f8fafc" }}>
                          ₹{log.ltp_at_signal?.toFixed(2)}
                        </td>
                        <td style={{ padding: "10px", textAlign: "right", color: "#64748b" }}>
                          ₹{log.baseline_ltp?.toFixed(2)}
                        </td>
                        <td style={{ padding: "10px", textAlign: "right", color: "#94a3b8" }}>
                          {(log.oi_at_signal || 0).toLocaleString("en-IN")}
                        </td>
                        <td style={{ padding: "10px", color: "#64748b", fontSize: "12px", maxWidth: "250px" }}>
                          {log.reason}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
