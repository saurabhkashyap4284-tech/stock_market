import { useState, useEffect } from "react";
import { signalsAPI, marketAPI } from "../api";
import Header from "../components/layout/Header";

export default function SignalsPage() {
  const [signals, setSignals] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    signalsAPI.history({ limit: 100 })
      .then(res => setSignals(res.data))
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  const handleDownload = async (type) => {
    try {
      const res = await marketAPI.downloadSignalLogs({ type });
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `signal_logs_${type || 'ALL'}.csv`);
      document.body.appendChild(link);
      link.click();
      link.parentNode.removeChild(link);
    } catch (err) {
      console.error("Download failed:", err);
      alert("Failed to download CSV");
    }
  };

  return (
    <div style={{ minHeight: "100vh", backgroundColor: "#0f172a" }}>
      <Header />
      <div style={{ padding: "20px" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "20px" }}>
          <h2 style={{ margin: 0 }}>Signal History</h2>
          <div style={{ display: "flex", gap: "10px" }}>
            <button onClick={() => handleDownload('BULLISH')} style={{ padding: "8px 12px", backgroundColor: "#22c55e", color: "#fff", border: "none", borderRadius: "4px", cursor: "pointer" }}>
              Download Bullish
            </button>
            <button onClick={() => handleDownload('BEARISH')} style={{ padding: "8px 12px", backgroundColor: "#ef4444", color: "#fff", border: "none", borderRadius: "4px", cursor: "pointer" }}>
              Download Bearish
            </button>
            <button onClick={() => handleDownload('FALSE_ALERTS')} style={{ padding: "8px 12px", backgroundColor: "#f59e0b", color: "#fff", border: "none", borderRadius: "4px", cursor: "pointer" }}>
              Download False Alerts
            </button>
          </div>
        </div>
        {loading ? (
          <p>Loading...</p>
        ) : (
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr style={{ borderBottom: "1px solid #334155" }}>
                <th style={{ padding: "10px", textAlign: "left" }}>Symbol</th>
                <th style={{ padding: "10px", textAlign: "left" }}>Signal</th>
                <th style={{ padding: "10px", textAlign: "left" }}>Time</th>
                <th style={{ padding: "10px", textAlign: "left" }}>Details</th>
              </tr>
            </thead>
            <tbody>
              {signals.map((sig, idx) => (
                <tr key={idx} style={{ borderBottom: "1px solid #334155" }}>
                  <td style={{ padding: "10px" }}>{sig.symbol}</td>
                  <td style={{ padding: "10px" }}>{sig.signal}</td>
                  <td style={{ padding: "10px" }}>{new Date(sig.created_at).toLocaleString()}</td>
                  <td style={{ padding: "10px", color: "#94a3b8" }}>LTP: ₹{sig.ltp}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
