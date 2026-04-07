import { useCallback, useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { getSectorLabel } from "@/lib/i18n";
import { cn, formatCompactNumber, formatPercent, getChangeColor } from "@/lib/utils";
import { api } from "@/lib/api";

interface MarketMoversProps {
  sectors: { name: string; etf_symbol: string }[];
  selectedSector: string | null;
}

interface StockData {
  symbol: string;
  name: string;
  close: number;
  change_p: number;
  volume: number;
  market_cap: number;
}

interface MoverItem {
  symbol: string;
  name: string;
  value: string;
  colorClass: string;
}

const CACHE_TTL_MS = 4 * 60 * 60 * 1000;

function MoverList({ title, items }: { title: string; items: MoverItem[] }) {
  if (items.length === 0) return null;

  return (
    <div>
      <h4 className="mb-2 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
        {title}
      </h4>
      <div className="space-y-1">
        {items.map((item) => (
          <div
            key={item.symbol}
            className="flex items-center justify-between rounded px-2 py-1 text-sm"
          >
            <div className="flex items-center gap-2">
              <span className="font-mono text-xs text-muted-foreground">{item.symbol}</span>
              <span className="text-foreground truncate max-w-[8rem]">{item.name}</span>
            </div>
            <span className={cn("font-mono text-xs", item.colorClass)}>{item.value}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

export function MarketMovers({ sectors, selectedSector }: MarketMoversProps) {
  const [stocks, setStocks] = useState<StockData[]>([]);
  const [loading, setLoading] = useState(false);

  const etfSymbol = sectors.find((s) => s.name === selectedSector)?.etf_symbol;

  const fetchStocks = useCallback(async () => {
    if (!etfSymbol) return;

    const cacheKey = `market_movers_${etfSymbol}`;
    const cached = localStorage.getItem(cacheKey);
    if (cached) {
      try {
        const { data, ts } = JSON.parse(cached) as { data: StockData[]; ts: number };
        if (Date.now() - ts < CACHE_TTL_MS) {
          setStocks(data);
          return;
        }
      } catch { /* fetch fresh */ }
    }

    setLoading(true);
    try {
      const data = await api.getSectorStocks(etfSymbol);
      const filtered = data.filter((s) => s.symbol !== "ETC");
      setStocks(filtered);
      localStorage.setItem(cacheKey, JSON.stringify({ data: filtered, ts: Date.now() }));
    } catch { /* ignore */ }
    setLoading(false);
  }, [etfSymbol]);

  useEffect(() => {
    fetchStocks();
  }, [fetchStocks]);

  if (!selectedSector) {
    return (
      <Card>
        <CardContent className="py-8 text-center text-sm text-muted-foreground">
          섹터를 클릭하면 구성종목 랭킹을 표시합니다
        </CardContent>
      </Card>
    );
  }

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>
            {getSectorLabel(selectedSector)} 구성종목 랭킹
          </CardTitle>
        </CardHeader>
        <CardContent className="grid grid-cols-1 gap-4 sm:grid-cols-3">
          {Array.from({ length: 3 }).map((_, i) => (
            <Skeleton key={i} className="h-32 w-full" />
          ))}
        </CardContent>
      </Card>
    );
  }

  // Deduplicate
  const seen = new Set<string>();
  const unique = stocks.filter((s) => {
    if (seen.has(s.symbol)) return false;
    seen.add(s.symbol);
    return true;
  });

  const topGainers: MoverItem[] = [...unique]
    .sort((a, b) => b.change_p - a.change_p)
    .slice(0, 5)
    .map((s) => ({
      symbol: s.symbol,
      name: s.name,
      value: formatPercent(s.change_p),
      colorClass: getChangeColor(s.change_p),
    }));

  const topLosers: MoverItem[] = [...unique]
    .sort((a, b) => a.change_p - b.change_p)
    .slice(0, 5)
    .map((s) => ({
      symbol: s.symbol,
      name: s.name,
      value: formatPercent(s.change_p),
      colorClass: getChangeColor(s.change_p),
    }));

  const topVolume: MoverItem[] = [...unique]
    .sort((a, b) => b.volume - a.volume)
    .slice(0, 5)
    .map((s) => ({
      symbol: s.symbol,
      name: s.name,
      value: formatCompactNumber(s.volume),
      colorClass: "text-foreground",
    }));

  return (
    <Card>
      <CardHeader>
        <CardTitle>
          {getSectorLabel(selectedSector)} 구성종목 랭킹 ({etfSymbol})
        </CardTitle>
      </CardHeader>
      <CardContent className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <MoverList title="TOP GAINERS" items={topGainers} />
        <MoverList title="TOP LOSERS" items={topLosers} />
        <MoverList title="TOP VOLUME" items={topVolume} />
      </CardContent>
    </Card>
  );
}
