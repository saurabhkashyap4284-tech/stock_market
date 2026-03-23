import { SIGNAL_META } from "../../utils";

export default function SignalBadge({ signal, size = "small" }) {
  const meta = SIGNAL_META[signal] || SIGNAL_META.NEUTRAL;
  const sizeStyle = size === "large" ? { padding: "8px 14px", fontSize: "14px" } : { padding: "4px 8px", fontSize: "12px" };

  return (
    <div
      style={{
        display: "inline-block",
        padding: sizeStyle.padding,
        borderRadius: "4px",
        backgroundColor: meta.bg,
        border: `1px solid ${meta.color}`,
        color: meta.color,
        fontWeight: "bold",
        fontSize: sizeStyle.fontSize,
        cursor: "pointer",
      }}
    >
      {meta.icon} {meta.label}
    </div>
  );
}
