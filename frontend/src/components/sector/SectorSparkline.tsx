import { useCallback, useEffect, useState } from "react";
import { Line, LineChart, ResponsiveContainer } from "recharts";
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
    return <div className="h-8 w-full" />;
  }

  const color = positive ? "#22c55e" : "#ef4444";

  return (
    <ResponsiveContainer width="100%" height={32}>
      <LineChart data={data} margin={{ top: 4, right: 2, bottom: 4, left: 2 }}>
        <Line
          type="monotone"
          dataKey="close"
          stroke={color}
          strokeWidth={1.5}
          dot={false}
          isAnimationActive={false}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}

export function SectorSparkline({ sectors, selectedSector, onSectorClick }: SectorSparklineProps) {
  const [historyMap, setHistoryMap] = useState<Record<string, SparkPoint[]>>({});
  const [loaded, setLoaded] = useState(false);

  const fetchAll = useCallback(async () => {
    // Check cache
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

  return (
    <div className="space-y-1">
      {sectors.map((sector) => {
        const history = historyMap[sector.etf_symbol] ?? [];
        return (
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
            <span className="w-20 shrink-0 text-sm font-medium text-foreground truncate">
              {getSectorLabel(sector.etf_symbol) !== sector.etf_symbol
                ? getSectorLabel(sector.etf_symbol)
                : sector.name}
            </span>
            <div className="min-w-0 flex-1">
              {loaded ? (
                <MiniChart data={history} positive={sector.change_percent >= 0} />
              ) : (
                <div className="h-8 w-full animate-pulse rounded bg-muted/30" />
              )}
            </div>
            <span className={cn("w-16 shrink-0 text-right font-mono text-xs", getChangeColor(sector.change_percent))}>
              {formatPercent(sector.change_percent)}
            </span>
          </button>
        );
      })}
    </div>
  );
}
