import { useEffect, useRef, useCallback } from "react";
import { useMarketStore, useAlertsStore } from "../store";
// ── Dynamic WS URL Logic ──────────────────────────────────────
const getWsUrl = () => {
  if (import.meta.env.VITE_WS_URL) return import.meta.env.VITE_WS_URL;
  const { protocol, host } = window.location;
  const wsProto = protocol === "https:" ? "wss:" : "ws:";
  // Default to the same host but with the /ws/market/ path
  return `${wsProto}//${host}/ws/market/`;
};

const WS_URL = getWsUrl();

export function useWebSocket() {
  const wsRef       = useRef(null);
  const retryRef    = useRef(0);
  const maxRetries  = 5;

  const updateFromWS   = useMarketStore(s => s.updateFromWS);
  const setInitialState= useMarketStore(s => s.setInitialState);
  const setWsConnected = useMarketStore(s => s.setWsConnected);
  const prevSignals    = useRef({});
  const addToast       = useAlertsStore(s => s.addToast);

  const connect = useCallback(() => {
    const token = localStorage.getItem("access_token");
    const url   = `${WS_URL}?token=${token}`;

    wsRef.current = new WebSocket(url);

    wsRef.current.onopen = () => {
      console.log("WebSocket connected ✅");
      setWsConnected(true);
      retryRef.current = 0;
    };

    wsRef.current.onmessage = (e) => {
      try {
        const msg = JSON.parse(e.data);

        if (msg.type === "initial_state") {
          setInitialState(msg);
        }

        if (msg.type === "market_update") {
          updateFromWS(msg);

          // Toast alerts — signal badla to notify karo
          msg.stocks?.forEach(s => {
            const prev = prevSignals.current[s.symbol];
            const curr = s.signal?.signal;
            if (curr && curr !== "NEUTRAL" && prev !== curr) {
              addToast({ symbol: s.symbol, ...s.signal, ltp: s.ltp });
            }
            prevSignals.current[s.symbol] = curr;
          });
        }
      } catch (err) {
        console.error("WS parse error:", err);
      }
    };

    wsRef.current.onclose = (e) => {
      console.warn("WebSocket closed:", e.code);
      setWsConnected(false);

      // Auto-reconnect with backoff
      if (retryRef.current < maxRetries) {
        const delay = Math.min(1000 * 2 ** retryRef.current, 30000);
        retryRef.current++;
        console.log(`Reconnecting in ${delay}ms (attempt ${retryRef.current})`);
        setTimeout(connect, delay);
      }
    };

    wsRef.current.onerror = (err) => {
      console.error("WebSocket error:", err);
    };
  }, [updateFromWS, setInitialState, setWsConnected, addToast]);

  useEffect(() => {
    connect();
    return () => {
      wsRef.current?.close();
    };
  }, [connect]);

  const sendPing = () => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ action: "ping" }));
    }
  };

  return { sendPing };
}
