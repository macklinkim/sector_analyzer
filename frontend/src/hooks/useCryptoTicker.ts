import { useEffect, useRef, useState } from "react";

/**
 * Live ticker data streamed from Binance combined WebSocket. One connection serves all
 * tracked symbols; the hook reconnects on close and pauses when the tab is hidden so
 * mobile browsers don't hold an idle socket in the background.
 */
export interface CryptoTicker {
  symbol: string; // lowercase, matches coin_metadata.symbol (e.g. "btc")
  price: number;
  change24h: number; // percent, -5.43 means -5.43%
  volume24h: number; // quote volume (USDT)
  updatedAt: number; // epoch ms
}

const BINANCE_STREAM = "wss://stream.binance.com:9443/stream";
const RECONNECT_DELAY_MS = 3000;

/** Build a combined-stream URL like ``wss://.../stream?streams=btcusdt@ticker/ethusdt@ticker``. */
function buildStreamUrl(symbols: string[]): string {
  const streams = symbols.map((s) => `${s.toLowerCase()}usdt@ticker`).join("/");
  return `${BINANCE_STREAM}?streams=${streams}`;
}

export function useCryptoTicker(symbols: string[]): Record<string, CryptoTicker> {
  const [tickers, setTickers] = useState<Record<string, CryptoTicker>>({});
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimerRef = useRef<number | null>(null);
  const symbolsKey = symbols.slice().sort().join(",");

  useEffect(() => {
    if (!symbols.length) return;

    let closed = false;

    const connect = () => {
      if (closed) return;
      if (typeof document !== "undefined" && document.hidden) return; // wait for visibility

      const ws = new WebSocket(buildStreamUrl(symbols));
      wsRef.current = ws;

      ws.onmessage = (ev: MessageEvent<string>) => {
        try {
          const msg = JSON.parse(ev.data) as { stream?: string; data?: Record<string, unknown> };
          const data = msg.data;
          if (!data) return;

          // Binance ticker payload fields: s=symbol, c=close, P=priceChangePercent, q=quoteVolume
          const raw = String(data.s ?? "").toLowerCase();
          const symbol = raw.endsWith("usdt") ? raw.slice(0, -4) : raw;
          const price = Number(data.c);
          const change24h = Number(data.P);
          const volume24h = Number(data.q);
          if (!symbol || !Number.isFinite(price)) return;

          setTickers((prev) => ({
            ...prev,
            [symbol]: { symbol, price, change24h, volume24h, updatedAt: Date.now() },
          }));
        } catch {
          // ignore malformed frames
        }
      };

      ws.onclose = () => {
        wsRef.current = null;
        if (closed) return;
        reconnectTimerRef.current = window.setTimeout(connect, RECONNECT_DELAY_MS);
      };

      ws.onerror = () => {
        ws.close();
      };
    };

    const onVisibility = () => {
      if (document.hidden) {
        wsRef.current?.close();
      } else if (!wsRef.current) {
        connect();
      }
    };

    connect();
    document.addEventListener("visibilitychange", onVisibility);

    return () => {
      closed = true;
      document.removeEventListener("visibilitychange", onVisibility);
      if (reconnectTimerRef.current) window.clearTimeout(reconnectTimerRef.current);
      wsRef.current?.close();
      wsRef.current = null;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [symbolsKey]);

  return tickers;
}
