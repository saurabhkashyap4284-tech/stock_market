import { useState, useEffect } from "react";
import { alertsAPI } from "../api";
import Header from "../components/layout/Header";

export default function AlertsPage() {
  const [rules, setRules] = useState([]);
  const [loading, setLoading] = useState(true);
  const [newRule, setNewRule] = useState({ symbol: "", condition: "price_above", value: 0 });

  useEffect(() => {
    fetchRules();
  }, []);

  const fetchRules = async () => {
    try {
      const res = await alertsAPI.getRules();
      setRules(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateRule = async (e) => {
    e.preventDefault();
    try {
      await alertsAPI.createRule(newRule);
      setNewRule({ symbol: "", condition: "price_above", value: 0 });
      fetchRules();
    } catch (err) {
      console.error(err);
    }
  };

  const handleDeleteRule = async (id) => {
    try {
      await alertsAPI.deleteRule(id);
      fetchRules();
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div style={{ minHeight: "100vh", backgroundColor: "#0f172a" }}>
      <Header />
      <div style={{ padding: "20px", maxWidth: "1000px", margin: "0 auto" }}>
        <h2>Alert Rules</h2>

        <form onSubmit={handleCreateRule} style={{ marginBottom: "20px", padding: "15px", backgroundColor: "#1e293b", borderRadius: "8px" }}>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr auto", gap: "10px", marginBottom: "10px" }}>
            <input
              type="text"
              placeholder="Symbol"
              value={newRule.symbol}
              onChange={(e) => setNewRule({ ...newRule, symbol: e.target.value.toUpperCase() })}
              style={{ padding: "8px", borderRadius: "4px", border: "1px solid #475569", backgroundColor: "#0f172a", color: "white" }}
              required
            />
            <select
              value={newRule.condition}
              onChange={(e) => setNewRule({ ...newRule, condition: e.target.value })}
              style={{ padding: "8px", borderRadius: "4px", border: "1px solid #475569", backgroundColor: "#0f172a", color: "white" }}
            >
              <option>price_above</option>
              <option>price_below</option>
              <option>signal_change</option>
            </select>
            <input
              type="number"
              placeholder="Value"
              value={newRule.value}
              onChange={(e) => setNewRule({ ...newRule, value: e.target.value })}
              style={{ padding: "8px", borderRadius: "4px", border: "1px solid #475569", backgroundColor: "#0f172a", color: "white" }}
            />
            <button
              type="submit"
              style={{ padding: "8px 16px", backgroundColor: "#00f5a0", border: "none", borderRadius: "4px", cursor: "pointer", fontWeight: "bold" }}
            >
              Add Rule
            </button>
          </div>
        </form>

        {loading ? (
          <p>Loading...</p>
        ) : (
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr style={{ borderBottom: "1px solid #334155" }}>
                <th style={{ padding: "10px", textAlign: "left" }}>Symbol</th>
                <th style={{ padding: "10px", textAlign: "left" }}>Condition</th>
                <th style={{ padding: "10px", textAlign: "left" }}>Value</th>
                <th style={{ padding: "10px", textAlign: "left" }}>Action</th>
              </tr>
            </thead>
            <tbody>
              {rules.map((rule) => (
                <tr key={rule.id} style={{ borderBottom: "1px solid #334155" }}>
                  <td style={{ padding: "10px" }}>{rule.symbol}</td>
                  <td style={{ padding: "10px" }}>{rule.condition}</td>
                  <td style={{ padding: "10px" }}>{rule.value}</td>
                  <td style={{ padding: "10px" }}>
                    <button
                      onClick={() => handleDeleteRule(rule.id)}
                      style={{ padding: "5px 10px", backgroundColor: "#ff4757", color: "white", border: "none", borderRadius: "4px", cursor: "pointer" }}
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
