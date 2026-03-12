import { useMarketStore } from "../store";
import { PHASE_META, SIGNAL_META } from "../utils";

export default function DashboardWidgets() {
  const { phase, getCounts } = useMarketStore();
  const counts = getCounts();
  const phaseMeta = PHASE_META[phase] || PHASE_META.PRE;

  const cards = [
    { key: "BEARISH", count: counts.BEARISH, meta: SIGNAL_META.BEARISH },
    { key: "BEARISH_ZONE", count: counts.BEARISH_ZONE, meta: SIGNAL_META.BEARISH_ZONE },
    { key: "BULLISH", count: counts.BULLISH, meta: SIGNAL_META.BULLISH },
    { key: "BULLISH_ZONE", count: counts.BULLISH_ZONE, meta: SIGNAL_META.BULLISH_ZONE },
  ];

  return (
    <div style={{ padding: "20px" }}>
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

      {/* Signal Cards */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "15px" }}>
        {cards.map(card => (
          <div
            key={card.key}
            style={{
              padding: "20px",
              borderRadius: "8px",
              backgroundColor: card.meta.bg,
              border: `2px solid ${card.meta.color}`,
              textAlign: "center",
            }}
          >
            <div style={{ fontSize: "32px", marginBottom: "10px" }}>{card.meta.icon}</div>
            <div style={{ fontSize: "24px", fontWeight: "bold", color: card.meta.color }}>{card.count}</div>
            <div style={{ fontSize: "12px", color: "#94a3b8" }}>{card.meta.label}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
