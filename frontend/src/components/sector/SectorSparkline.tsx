import { useCallback, useEffect, useState } from "react";
import { Line, LineChart, ResponsiveContainer, Tooltip } from "recharts";
import { getSectorLabel } from "@/lib/i18n";
import { cn } from "@/lib/utils";
import { formatPercent, getChangeColor } from "@/lib/utils";
import type { Sector } from "@/types";

interface SectorSparklineProps {
  sectors: Sector[];
  selectedSector: string | null;
  onSectorClick: (sectorName: string) => void;
}

interface SparkPoint {
  date: string;
  close: number;
}

const CACHE_TTL_MS = 4 * 60 * 60 * 1000; // 4 hours

function SparklineChart({ etfSymbol, positive }: { etfSymbol: string; positive: boolean }) {
  const [data, setData] = useState<SparkPoint[]>([]);

  const fetchData = useCallback(async () => {
    const cacheKey = `sparkline_${etfSymbol}`;
    const cached = localStorage.getItem(cacheKey);
    if (cached) {
      try {
        const { data: cachedData, ts } = JSON.parse(cached) as { data: SparkPoint[]; ts: number };
        if (Date.now() - ts < CACHE_TTL_MS) {
          setData(cachedData);
          return;
        }
      } catch { /* fetch fresh */ }
    }

    try {
      const resp = await fetch(`/api/market/sector-history/${etfSymbol}?days=7`);
      if (resp.ok) {
        const points: SparkPoint[] = await resp.json();
        setData(points);
        localStorage.setItem(cacheKey, JSON.stringify({ data: points, ts: Date.now() }));
      }
    } catch { /* ignore */ }
  }, [etfSymbol]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  if (data.length === 0) return null;

  const color = positive ? "var(--color-bullish)" : "var(--color-bearish)";

  return (
    <ResponsiveContainer width="100%" height={32}>
      <LineChart data={data}>
        <Tooltip
          contentStyle={{
            backgroundColor: "var(--color-card)",
            border: "1px solid var(--color-border)",
            borderRadius: 6,
            fontSize: 11,
            color: "var(--color-foreground)",
          }}
          formatter={(value) => [`$${(value as number).toFixed(2)}`, "가격"]}
          labelFormatter={(label) => label}
        />
        <Line
          type="monotone"
          dataKey="close"
          stroke={color}
          strokeWidth={1.5}
          dot={false}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}

export function SectorSparkline({ sectors, selectedSector, onSectorClick }: SectorSparklineProps) {
  return (
    <div className="space-y-1">
      {sectors.map((sector) => (
        <button
          key={sector.etf_symbol}
          onClick={() => onSectorClick(sector.name)}
          className={cn(
            "flex w-full items-center gap-3 rounded-lg px-3 py-2 text-left transition-colors hover:bg-muted/50",
            selectedSector === sector.name && "bg-muted/70",
          )}
        >
          <span className="w-10 shrink-0 font-mono text-xs text-muted-foreground">
            {sector.etf_symbol}
          </span>
          <span className="w-20 shrink-0 text-sm font-medium text-foreground">
            {getSectorLabel(sector.etf_symbol) !== sector.etf_symbol
              ? getSectorLabel(sector.etf_symbol)
              : sector.name}
          </span>
          <div className="min-w-0 flex-1">
            <SparklineChart etfSymbol={sector.etf_symbol} positive={sector.change_percent >= 0} />
          </div>
          <span className={cn("w-16 shrink-0 text-right font-mono text-xs", getChangeColor(sector.change_percent))}>
            {formatPercent(sector.change_percent)}
          </span>
        </button>
      ))}
    </div>
  );
}
