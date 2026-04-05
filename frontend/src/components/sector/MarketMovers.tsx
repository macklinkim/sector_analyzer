import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { getSectorLabel } from "@/lib/i18n";
import { cn } from "@/lib/utils";
import { formatCompactNumber, formatPercent, getChangeColor } from "@/lib/utils";
import type { Sector } from "@/types";

interface MarketMoversProps {
  sectors: Sector[];
  selectedSector: string | null;
}

interface MoverItem {
  symbol: string;
  name: string;
  value: string;
  colorClass: string;
}

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
              <span className="text-foreground">{item.name}</span>
            </div>
            <span className={cn("font-mono text-xs", item.colorClass)}>{item.value}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

export function MarketMovers({ sectors, selectedSector }: MarketMoversProps) {
  if (!selectedSector) {
    return (
      <Card>
        <CardContent className="py-8 text-center text-sm text-muted-foreground">
          섹터를 클릭하면 Market Movers를 표시합니다
        </CardContent>
      </Card>
    );
  }

  // NOTE: 현재 섹터 ETF 레벨 데이터만 표시. 개별 종목 데이터는 향후 API 확장 시 추가.
  const topGainers: MoverItem[] = [...sectors]
    .sort((a, b) => b.change_percent - a.change_percent)
    .slice(0, 5)
    .map((s) => ({
      symbol: s.etf_symbol,
      name: getSectorLabel(s.etf_symbol),
      value: formatPercent(s.change_percent),
      colorClass: getChangeColor(s.change_percent),
    }));

  const topLosers: MoverItem[] = [...sectors]
    .sort((a, b) => a.change_percent - b.change_percent)
    .slice(0, 5)
    .map((s) => ({
      symbol: s.etf_symbol,
      name: getSectorLabel(s.etf_symbol),
      value: formatPercent(s.change_percent),
      colorClass: getChangeColor(s.change_percent),
    }));

  const topVolume: MoverItem[] = [...sectors]
    .sort((a, b) => b.volume - a.volume)
    .slice(0, 5)
    .map((s) => ({
      symbol: s.etf_symbol,
      name: getSectorLabel(s.etf_symbol),
      value: formatCompactNumber(s.volume),
      colorClass: "text-foreground",
    }));

  return (
    <Card>
      <CardHeader>
        <CardTitle>Sector Rankings — {selectedSector}</CardTitle>
      </CardHeader>
      <CardContent className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <MoverList title="Top Gainers" items={topGainers} />
        <MoverList title="Top Losers" items={topLosers} />
        <MoverList title="Top Volume" items={topVolume} />
      </CardContent>
    </Card>
  );
}
