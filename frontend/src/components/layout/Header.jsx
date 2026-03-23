import { useAuth } from "../../hooks/useAuth";
import { useMarketStore } from "../../store";
import { PHASE_META } from "../../utils";

export default function Header() {
  const { user, handleLogout } = useAuth();
  const { phase, wsConnected } = useMarketStore();
  const phaseMeta = PHASE_META[phase] || PHASE_META.PRE;

  return (
    <header style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "15px 20px", backgroundColor: "#1e293b", borderBottom: "1px solid #334155" }}>
      <div style={{ display: "flex", alignItems: "center", gap: "15px" }}>
        <h1 style={{ margin: 0, fontSize: "24px" }}>FO Monitor</h1>
        <div style={{ padding: "5px 10px", borderRadius: "4px", backgroundColor: phaseMeta.color + "20", border: `1px solid ${phaseMeta.color}` }}>
          {phaseMeta.label}
        </div>
        <div style={{ fontSize: "12px", color: wsConnected ? "#00f5a0" : "#ff4757" }}>
          {wsConnected ? "🟢 Connected" : "🔴 Disconnected"}
        </div>
      </div>
      <div style={{ display: "flex", alignItems: "center", gap: "15px" }}>
        <span>{user?.email}</span>
        <button onClick={handleLogout} style={{ padding: "8px 15px", backgroundColor: "#ff4757", border: "none", borderRadius: "4px", cursor: "pointer", color: "white" }}>
          Logout
        </button>
      </div>
    </header>
  );
}
