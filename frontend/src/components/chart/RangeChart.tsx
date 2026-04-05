import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { getSectorLabel } from "@/lib/i18n";
import { formatPrice } from "@/lib/utils";
import type { Sector } from "@/types";

interface RangeChartProps {
  sectors: Sector[];
  loading: boolean;
}

function BulletBar({ sector, estimated }: { sector: Sector; estimated: boolean }) {
  const current = sector.price;
  const low = estimated ? current * 0.8 : sector.week_52_low!;
  const high = estimated ? current * 1.2 : sector.week_52_high!;

  if (low >= high) return null;

  const positionPercent = Math.min(Math.max(((current - low) / (high - low)) * 100, 0), 100);

  return (
    <div className="grid grid-cols-[4.5rem_4rem_1fr_4rem_4.5rem] items-center gap-2 py-1.5">
      {/* Sector label */}
      <span className="text-xs font-medium text-foreground truncate">
        {getSectorLabel(sector.etf_symbol)}
        {estimated && <span className="text-[9px] text-muted-foreground ml-0.5">*</span>}
      </span>

      {/* Low price */}
      <span className="text-right font-mono text-[11px] text-muted-foreground">
        {formatPrice(low)}
      </span>

      {/* Range track */}
      <div className="relative h-5 rounded-full bg-slate-700/60">
        {/* Progress fill: low → current */}
        <div
          className="absolute inset-y-0 left-0 rounded-full bg-emerald-500/70"
          style={{ width: `${positionPercent}%` }}
        />
        {/* Current price marker */}
        <div
          className="absolute top-0 h-5 w-1 rounded-full bg-white shadow-sm shadow-black/40"
          style={{ left: `calc(${positionPercent}% - 2px)` }}
        />
      </div>

      {/* High price */}
      <span className="font-mono text-[11px] text-muted-foreground">
        {formatPrice(high)}
      </span>

      {/* Current price */}
      <span className="text-right font-mono text-xs font-semibold text-emerald-400">
        {formatPrice(current)}
      </span>
    </div>
  );
}

export function RangeChart({ sectors, loading }: RangeChartProps) {
  if (loading) {
    return (
      <Card>
        <CardHeader><CardTitle>52주 범위 차트</CardTitle></CardHeader>
        <CardContent className="space-y-2">
          {Array.from({ length: 6 }).map((_, i) => (
            <Skeleton key={i} className="h-5 w-full" />
          ))}
        </CardContent>
      </Card>
    );
  }

  // Deduplicate by etf_symbol
  const seen = new Set<string>();
  const unique = sectors.filter((s) => {
    if (seen.has(s.etf_symbol)) return false;
    seen.add(s.etf_symbol);
    return true;
  });

  return (
    <Card>
      <CardHeader>
        <CardTitle>52주 범위 차트</CardTitle>
        <p className="text-xs text-muted-foreground">
          최저가 — 현재가 위치 — 최고가 (*추정 범위)
        </p>
      </CardHeader>
      <CardContent>
        {unique.map((sector) => {
          const hasReal = (sector.week_52_low ?? 0) > 0 && (sector.week_52_high ?? 0) > 0
            && sector.week_52_low! < sector.week_52_high!;
          return (
            <BulletBar
              key={sector.etf_symbol}
              sector={sector}
              estimated={!hasReal}
            />
          );
        })}
      </CardContent>
    </Card>
  );
}
