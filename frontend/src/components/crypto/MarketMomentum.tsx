import { useMemo } from "react";

import { cn } from "@/lib/utils";
import type { CoinMetadata } from "@/types";
import type { CryptoTicker } from "@/hooks/useCryptoTicker";

interface MarketMomentumProps {
  coins: CoinMetadata[];
  tickers: Record<string, CryptoTicker>;
}

interface Ranked {
  coin: CoinMetadata;
  ticker: CryptoTicker;
}

function formatVolume(vol: number): string {
  if (vol >= 1e9) return `$${(vol / 1e9).toFixed(1)}B`;
  if (vol >= 1e6) return `$${(vol / 1e6).toFixed(1)}M`;
  if (vol >= 1e3) return `$${(vol / 1e3).toFixed(1)}K`;
  return `$${vol.toFixed(0)}`;
}

/**
 * Derives "자금 쏠림" panels directly from the Binance WS ticker stream we already
 * subscribe to — no extra network cost. Inflow: top gainers weighted by quote volume.
 * Volatility: largest absolute moves regardless of direction.
 */
export function MarketMomentum({ coins, tickers }: MarketMomentumProps) {
  const { inflow, volatility, volumeThreshold } = useMemo(() => {
    const joined: Ranked[] = coins
      .map((c) => ({ coin: c, ticker: tickers[c.symbol] }))
      .filter((r): r is Ranked => !!r.ticker && Number.isFinite(r.ticker.price));

    // Volume spike threshold: anything above the 80th percentile of 24h quote volume
    const volumes = joined.map((r) => r.ticker.volume24h).sort((a, b) => a - b);
    const p80 = volumes.length > 0 ? volumes[Math.floor(volumes.length * 0.8)] : 0;

    const inflow = [...joined]
      .filter((r) => r.ticker.change24h > 0)
      // score: positive change scaled by relative volume share
      .sort(
        (a, b) =>
          b.ticker.change24h * Math.sqrt(b.ticker.volume24h) -
          a.ticker.change24h * Math.sqrt(a.ticker.volume24h),
      )
      .slice(0, 3);

    const volatility = [...joined]
      .sort((a, b) => Math.abs(b.ticker.change24h) - Math.abs(a.ticker.change24h))
      .slice(0, 3);

    return { inflow, volatility, volumeThreshold: p80 };
  }, [coins, tickers]);

  if (inflow.length === 0 && volatility.length === 0) return null;

  return (
    <div className="rounded-xl border border-slate-700/60 bg-slate-900/50 p-3 shadow-2xl backdrop-blur-md sm:p-4">
      <div className="mb-3 flex items-center justify-between">
        <h3 className="flex items-center gap-2 text-sm font-semibold text-foreground">
          <span
            aria-hidden
            className="inline-block h-2 w-2 animate-pulse rounded-full bg-sky-400 shadow-[0_0_8px_rgba(56,189,248,0.9)]"
          />
          실시간 자금 쏠림
        </h3>
        <span className="text-[10px] text-muted-foreground">Binance · 24h 기준</span>
      </div>

      <div className="grid grid-cols-2 gap-2 sm:gap-3">
        <Panel
          title="상승 주도"
          items={inflow}
          volumeThreshold={volumeThreshold}
          tone="bullish"
        />
        <Panel
          title="변동성 상위"
          items={volatility}
          volumeThreshold={volumeThreshold}
          tone="volatility"
        />
      </div>
    </div>
  );
}

function Panel({
  title,
  items,
  volumeThreshold,
  tone,
}: {
  title: string;
  items: Ranked[];
  volumeThreshold: number;
  tone: "bullish" | "volatility";
}) {
  const borderTone =
    tone === "bullish" ? "border-emerald-500/30 bg-emerald-500/5" : "border-rose-500/25 bg-rose-500/5";
  const accentTone = tone === "bullish" ? "text-emerald-400" : "text-rose-400";

  return (
    <div className={cn("rounded-lg border p-2 sm:p-3", borderTone)}>
      <p className={cn("mb-2 text-[10px] font-semibold uppercase tracking-wider", accentTone)}>
        {title}
      </p>
      <ul className="space-y-1.5">
        {items.length === 0 ? (
          <li className="text-xs text-muted-foreground">—</li>
        ) : (
          items.map(({ coin, ticker }) => {
            const isSurge = ticker.volume24h >= volumeThreshold && volumeThreshold > 0;
            const changeColor =
              ticker.change24h >= 0 ? "text-emerald-400" : "text-rose-400";
            return (
              <li
                key={coin.coin_id}
                className={cn(
                  "flex items-center justify-between gap-2 rounded-md px-1.5 py-1",
                  isSurge && "ring-1 ring-amber-400/50 shadow-[0_0_10px_rgba(251,191,36,0.25)]",
                )}
              >
                <div className="flex min-w-0 items-center gap-1.5">
                  {coin.image_url && (
                    <img
                      src={coin.image_url}
                      alt={coin.symbol}
                      className="h-4 w-4 shrink-0 rounded-full"
                    />
                  )}
                  <span className="font-mono text-xs font-semibold text-foreground">
                    {coin.symbol.toUpperCase()}
                  </span>
                  {isSurge && (
                    <span
                      aria-hidden
                      className="inline-block h-1.5 w-1.5 animate-pulse rounded-full bg-amber-400"
                      title="거래량 상위"
                    />
                  )}
                </div>
                <div className="flex shrink-0 flex-col items-end">
                  <span className={cn("font-mono text-xs font-bold tabular-nums", changeColor)}>
                    {ticker.change24h >= 0 ? "+" : ""}
                    {ticker.change24h.toFixed(2)}%
                  </span>
                  <span className="font-mono text-[9px] text-muted-foreground tabular-nums">
                    {formatVolume(ticker.volume24h)}
                  </span>
                </div>
              </li>
            );
          })
        )}
      </ul>
    </div>
  );
}
