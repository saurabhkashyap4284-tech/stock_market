import { useMarketStore } from "../../store";
import { PHASE_META, SIGNAL_META } from "../../utils";
import { marketAPI } from "../../api";
import { useState, useEffect } from "react";

// ── Accuracy Gauge Component ──────────────────────────────────
function AccuracyGauge({ percent, color, label }) {
  const radius = 36;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (percent / 100) * circumference;

  return (
    <div style={{
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
      justifyContent: "center",
      padding: "15px",
      borderRadius: "12px",
      background: "rgba(30, 41, 59, 0.5)",
      border: `1px solid ${color}30`,
      flex: 1,
      minWidth: "140px",
      position: "relative"
    }}>
      <svg width="100" height="100" style={{ transform: "rotate(-90deg)" }}>
        {/* Background track */}
        <circle
          cx="50" cy="50" r={radius}
          fill="transparent"
          stroke="rgba(255,255,255,0.05)"
          strokeWidth="8"
        />
        {/* Progress bar */}
        <circle
          cx="50" cy="50" r={radius}
          fill="transparent"
          stroke={color}
          strokeWidth="8"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          style={{ transition: "stroke-dashoffset 0.8s ease-in-out" }}
        />
      </svg>
      <div style={{
        position: "absolute",
        top: "42px",
        fontSize: "18px",
        fontWeight: "bold",
        color: "#f8fafc"
      }}>
        {percent}%
      </div>
      <div style={{ marginTop: "5px", fontSize: "11px", fontWeight: "600", color: "#94a3b8", textTransform: "uppercase", letterSpacing: "0.5px" }}>
        {label}
      </div>
    </div>
  );
}

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
    // Mapping internal keys to API keys if necessary
    const apiType = key === "FALSE_ALERTS" ? "FALSE_ALERTS" : 
                    key === "BEARISH" ? "BEARISH_FALL" : 
                    key === "BULLISH" ? "BULLISH_BREAKOUT" : key;
    setSelectedKPI(selectedKPI === apiType ? null : apiType);
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

  const handleDownload = async (type) => {
    try {
      const res = await marketAPI.downloadSignalLogs({ type });
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement('a');
      link.href = url;
      const dateStr = new Date().toISOString().split('T')[0];
      link.setAttribute('download', `signal_logs_${type || 'ALL'}_${dateStr}.csv`);
      document.body.appendChild(link);
      link.click();
      link.parentNode.removeChild(link);
    } catch (err) {
      console.error("Download failed:", err);
      alert("Failed to download CSV");
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

      {/* Main Grid: Phase + Accuracy */}
      <div style={{ display: "flex", flexWrap: "wrap", gap: "20px", marginBottom: "20px" }}>
        {/* Phase Banner */}
        <div
          style={{
            flex: "2 1 400px",
            padding: "20px",
            borderRadius: "12px",
            backgroundColor: phaseMeta.color + "15",
            border: `2px solid ${phaseMeta.color}`,
            display: "flex",
            flexDirection: "column",
            justifyContent: "center"
          }}
        >
          <div style={{ fontSize: "20px", fontWeight: "bold", marginBottom: "5px", color: phaseMeta.color }}>{phaseMeta.label}</div>
          <div style={{ color: "#94a3b8", fontSize: "14px" }}>{phaseMeta.desc}</div>
        </div>

        {/* Accuracy Section */}
        <div style={{ flex: "1 1 300px", display: "flex", gap: "15px" }}>
          <AccuracyGauge 
            percent={counts.BULLISH_ACCURACY} 
            color={SIGNAL_META.BULLISH.color} 
            label="Bullish Accuracy" 
          />
          <AccuracyGauge 
            percent={counts.BEARISH_ACCURACY} 
            color={SIGNAL_META.BEARISH.color} 
            label="Bearish Accuracy" 
          />
        </div>
      </div>

      {/* KPI Signal Cards — Clickable */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "15px" }}>
        {cards.map(card => {
          const apiType = card.key === "FALSE_ALERTS" ? "FALSE_ALERTS" : 
                         card.key === "BEARISH" ? "BEARISH_FALL" : 
                         card.key === "BULLISH" ? "BULLISH_BREAKOUT" : card.key;
          const isActive = selectedKPI === apiType;

          return (
            <div
              key={card.key}
              onClick={() => handleCardClick(card.key)}
              style={{
                padding: "20px",
                borderRadius: "12px",
                backgroundColor: isActive ? card.meta.bg.replace("0.08", "0.25").replace("0.1", "0.25") : card.meta.bg,
                border: `2px solid ${isActive ? card.meta.color : (card.meta.border || card.meta.color + "50")}`,
                textAlign: "center",
                cursor: "pointer",
                transition: "all 0.2s ease",
                transform: isActive ? "scale(1.02)" : "scale(1)",
                boxShadow: isActive ? `0 4px 20px ${card.meta.color}30` : "none",
              }}
            >
              <div style={{ fontSize: "32px", marginBottom: "10px" }}>{card.meta.icon}</div>
              <div style={{ fontSize: "24px", fontWeight: "bold", color: card.meta.color }}>{card.count}</div>
              <div style={{ fontSize: "12px", color: "#94a3b8", fontWeight: "600", marginTop: "4px" }}>{card.meta.label}</div>
              <div style={{ fontSize: "10px", color: "#64748b", marginTop: "8px", fontStyle: "italic" }}>
                {isActive ? "▲ Click to close" : "Click to view stocks"}
              </div>
            </div>
          );
        })}
      </div>

      {/* Drilldown Panel — Shows when a KPI card is selected */}
      {selectedKPI && (
        <div style={{
          marginTop: "20px",
          padding: "20px",
          borderRadius: "12px",
          backgroundColor: "#1e293b",
          border: "1px solid #334155",
          boxShadow: "0 10px 30px rgba(0,0,0,0.3)"
        }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "15px" }}>
            <h3 style={{ margin: 0, color: "#f8fafc", display: "flex", alignItems: "center", gap: "10px" }}>
              {selectedKPI === "FALSE_ALERTS" ? "❌ False Alerts" : 
               (SIGNAL_META[selectedKPI.split('_')[0]]?.icon || "🔍") + " " + selectedKPI.replace("_", " ")} — Detail
            </h3>
            <div style={{ display: "flex", gap: "10px" }}>
              <button
                onClick={() => handleDownload(selectedKPI)}
                style={{
                  padding: "6px 14px",
                  backgroundColor: "#2563eb",
                  color: "white",
                  border: "none",
                  borderRadius: "6px",
                  cursor: "pointer",
                  fontSize: "12px",
                  fontWeight: "bold",
                  transition: "background 0.2s",
                }}
              >
                📥 Download CSV
              </button>
              <button
                onClick={() => setSelectedKPI(null)}
                style={{
                  padding: "6px 14px",
                  backgroundColor: "#475569",
                  color: "white",
                  border: "none",
                  borderRadius: "6px",
                  cursor: "pointer",
                  fontSize: "12px",
                }}
              >
                ✕ Close
              </button>
            </div>
          </div>

          {loadingDrilldown ? (
            <p style={{ color: "#94a3b8" }}>Loading signal logs...</p>
          ) : drilldownData.length === 0 ? (
            <p style={{ color: "#64748b" }}>No signal logs found for today.</p>
          ) : (
            <div style={{ maxHeight: "400px", overflowY: "auto", borderRadius: "8px", border: "1px solid #334155" }}>
              <table style={{ width: "100%", borderCollapse: "collapse" }}>
                <thead>
                  <tr style={{ borderBottom: "2px solid #475569", position: "sticky", top: 0, backgroundColor: "#1e293b", zIndex: 1 }}>
                    <th style={{ padding: "12px", textAlign: "left", color: "#94a3b8", fontSize: "11px", textTransform: "uppercase" }}>Symbol</th>
                    <th style={{ padding: "12px", textAlign: "left", color: "#94a3b8", fontSize: "11px", textTransform: "uppercase" }}>Signal</th>
                    <th style={{ padding: "12px", textAlign: "left", color: "#94a3b8", fontSize: "11px", textTransform: "uppercase" }}>Time</th>
                    <th style={{ padding: "12px", textAlign: "right", color: "#94a3b8", fontSize: "11px", textTransform: "uppercase" }}>LTP</th>
                    <th style={{ padding: "12px", textAlign: "right", color: "#94a3b8", fontSize: "11px", textTransform: "uppercase" }}>Baseline</th>
                    <th style={{ padding: "12px", textAlign: "right", color: "#94a3b8", fontSize: "11px", textTransform: "uppercase" }}>OI</th>
                    <th style={{ padding: "12px", textAlign: "left", color: "#94a3b8", fontSize: "11px", textTransform: "uppercase" }}>Reason</th>
                  </tr>
                </thead>
                <tbody>
                  {drilldownData.map((log, idx) => {
                    // Map BULLISH_BREAKOUT or BEARISH_FALL to the base type for meta
                    const baseType = log.signal_type.split('_')[0];
                    const sigMeta = SIGNAL_META[baseType] || SIGNAL_META.NEUTRAL;
                    
                    return (
                      <tr key={log.id || idx} style={{ borderBottom: "1px solid #334155", transition: "background 0.2s" }} onMouseOver={e => e.currentTarget.style.backgroundColor = "#1e293b"}>
                        <td style={{ padding: "12px", fontWeight: "bold", color: "#f8fafc" }}>{log.symbol}</td>
                        <td style={{ padding: "12px" }}>
                          <span style={{
                            padding: "4px 10px",
                            borderRadius: "6px",
                            backgroundColor: sigMeta.bg,
                            color: sigMeta.color,
                            fontSize: "10px",
                            fontWeight: "bold",
                            border: `1px solid ${sigMeta.border}`,
                            whiteSpace: "nowrap"
                          }}>
                            {sigMeta.icon} {log.signal_type.replace("_", " ")}
                          </span>
                        </td>
                        <td style={{ padding: "12px", color: "#94a3b8", fontSize: "13px" }}>
                          {new Date(log.timestamp).toLocaleTimeString("en-IN", { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                        </td>
                        <td style={{ padding: "12px", textAlign: "right", color: "#f8fafc", fontFamily: "monospace" }}>
                          ₹{log.ltp_at_signal?.toFixed(2)}
                        </td>
                        <td style={{ padding: "12px", textAlign: "right", color: "#64748b", fontFamily: "monospace" }}>
                          ₹{log.baseline_ltp?.toFixed(2)}
                        </td>
                        <td style={{ padding: "12px", textAlign: "right", color: "#94a3b8", fontFamily: "monospace" }}>
                          {(log.oi_at_signal || 0).toLocaleString("en-IN")}
                        </td>
                        <td style={{ padding: "12px", color: "#64748b", fontSize: "12px", maxWidth: "300px", lineHeight: "1.4" }}>
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
