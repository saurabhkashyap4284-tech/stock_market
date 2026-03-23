import { useEffect } from "react";
import { useAlertsStore } from "../../store";export default function AlertToasts() {
  const { toasts, removeToast } = useAlertsStore();

  useEffect(() => {
    const timers = toasts.map(t => setTimeout(() => removeToast(t.id), 5000));
    return () => timers.forEach(clearTimeout);
  }, [toasts, removeToast]);

  return (
    <div style={{ position: "fixed", bottom: "20px", right: "20px", zIndex: 9999 }}>
      {toasts.map(t => (
        <div
          key={t.id}
          style={{
            padding: "12px 16px",
            marginBottom: "10px",
            borderRadius: "6px",
            backgroundColor: t.signal?.color || "#64748b",
            color: "white",
            boxShadow: "0 4px 12px rgba(0,0,0,0.3)",
            animation: "slideIn 0.3s ease-out",
          }}
        >
          <div style={{ fontWeight: "bold" }}>{t.symbol}</div>
          <div>{t.signal?.label || "Update"}</div>
          <div style={{ fontSize: "12px", opacity: 0.8 }}>₹{t.ltp}</div>
        </div>
      ))}
    </div>
  );
}
