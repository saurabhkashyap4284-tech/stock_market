import { useState, useEffect } from "react";
import { signalsAPI } from "../api";
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

  return (
    <div style={{ minHeight: "100vh", backgroundColor: "#0f172a" }}>
      <Header />
      <div style={{ padding: "20px" }}>
        <h2>Signal History</h2>
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
