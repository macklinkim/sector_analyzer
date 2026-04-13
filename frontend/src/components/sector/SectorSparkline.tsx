import { useCallback, useEffect, useState } from "react";
import { Area, AreaChart, ResponsiveContainer, Tooltip, YAxis } from "recharts";
import { getSectorLabel } from "@/lib/i18n";
import { cn } from "@/lib/utils";
import { formatPercent, getChangeColor } from "@/lib/utils";
import { api } from "@/lib/api";
import type { Sector, SectorWithHistory, SparkPoint } from "@/types";

interface SectorSparklineProps {
  sectors: Sector[];
  selectedSector: string | null;
  onSectorClick: (sectorName: string) => void;
}

const CACHE_KEY = "sparkline_all";
const CACHE_TTL_MS = 4 * 60 * 60 * 1000;

function MiniChart({ data, positive }: { data: SparkPoint[]; positive: boolean }) {
  if (data.length < 2) {
    return <div className="h-[62px] w-full" />;
  }

  const lineColor = positive ? "#22c55e" : "#ef4444";
  const gradientId = positive ? "sparkGreen" : "sparkRed";
  const firstDate = data[0].date;
  const lastDate = data[data.length - 1].date;

  // Add padding to Y domain
  const closes = data.map((d) => d.close);
  const minVal = Math.min(...closes);
  const maxVal = Math.max(...closes);
  const padding = (maxVal - minVal) * 0.15 || 1;

  return (
    <div className="relative">
      <ResponsiveContainer width="100%" height={62}>
        <AreaChart data={data} margin={{ top: 4, right: 2, bottom: 0, left: 2 }}>
          <defs>
            <linearGradient id={gradientId} x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={lineColor} stopOpacity={0.35} />
              <stop offset="100%" stopColor={lineColor} stopOpacity={0.03} />
            </linearGradient>
          </defs>
          <YAxis
            domain={[minVal - padding, maxVal + padding]}
            hide={true}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: "var(--color-card)",
              border: "1px solid var(--color-border)",
              borderRadius: 6,
              fontSize: 11,
              color: "var(--color-foreground)",
              padding: "4px 8px",
            }}
            formatter={(value) => [`$${(value as number).toFixed(2)}`, "가격"]}
            labelFormatter={(_, payload) => {
              if (payload?.[0]?.payload?.date) return payload[0].payload.date;
              return "";
            }}
            isAnimationActive={false}
          />
          <Area
            type="monotone"
            dataKey="close"
            stroke={lineColor}
            strokeWidth={1.5}
            fill={`url(#${gradientId})`}
            dot={false}
            isAnimationActive={false}
          />
        </AreaChart>
      </ResponsiveContainer>
      {/* Fixed date labels */}
      <div className="flex justify-between px-1 -mt-1">
        <span className="text-[9px] text-slate-500">{firstDate}</span>
        <span className="text-[9px] text-slate-500">{lastDate}</span>
      </div>
    </div>
  );
}

export function SectorSparkline({ sectors, selectedSector, onSectorClick }: SectorSparklineProps) {
  const [historyMap, setHistoryMap] = useState<Record<string, SparkPoint[]>>({});
  const [loaded, setLoaded] = useState(false);

  const fetchAll = useCallback(async () => {
    const cached = localStorage.getItem(CACHE_KEY);
    if (cached) {
      try {
        const { data, ts } = JSON.parse(cached) as { data: Record<string, SparkPoint[]>; ts: number };
        if (Date.now() - ts < CACHE_TTL_MS) {
          setHistoryMap(data);
          setLoaded(true);
          return;
        }
      } catch { /* fetch fresh */ }
    }

    try {
      const result: SectorWithHistory[] = await api.getSectorsWithHistory(30);
      const map: Record<string, SparkPoint[]> = {};
      for (const s of result) {
        map[s.sector] = s.history;
      }
      setHistoryMap(map);
      localStorage.setItem(CACHE_KEY, JSON.stringify({ data: map, ts: Date.now() }));
    } catch { /* ignore */ }
    setLoaded(true);
  }, []);

  useEffect(() => {
    fetchAll();
  }, [fetchAll]);

  // Deduplicate
  const seen = new Set<string>();
  const unique = sectors.filter((s) => {
    if (seen.has(s.etf_symbol)) return false;
    seen.add(s.etf_symbol);
    return true;
  });

  return (
    <div className="space-y-1">
      {unique.map((sector) => {
        const history = historyMap[sector.etf_symbol] ?? [];
        return (
          <button
            key={sector.etf_symbol}
            onClick={() => onSectorClick(sector.name)}
            className={cn(
              "grid w-full grid-cols-[2.5rem_5rem_1fr_3.5rem] items-center gap-2 rounded-lg px-3 py-2 text-left transition-colors hover:bg-muted/50",
              selectedSector === sector.name && "bg-muted/70",
            )}
          >
            <span className="font-mono text-[11px] text-muted-foreground">
              {sector.etf_symbol}
            </span>
            <span className="text-sm font-medium text-foreground truncate">
              {getSectorLabel(sector.etf_symbol) !== sector.etf_symbol
                ? getSectorLabel(sector.etf_symbol)
                : sector.name}
            </span>
            <div className="min-w-0">
              {loaded ? (
                <MiniChart data={history} positive={sector.change_percent >= 0} />
              ) : (
                <div className="h-[62px] w-full animate-pulse rounded bg-muted/30" />
              )}
            </div>
            <span className={cn("text-right font-mono text-xs font-medium", getChangeColor(sector.change_percent))}>
              {formatPercent(sector.change_percent)}
            </span>
          </button>
        );
      })}
    </div>
  );
}
