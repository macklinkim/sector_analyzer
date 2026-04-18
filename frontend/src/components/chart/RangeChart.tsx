import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { getSectorLabel } from "@/lib/i18n";
import { cn, formatPrice } from "@/lib/utils";
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
  const isNearHigh = positionPercent >= 70;
  const isNearLow = positionPercent <= 30;
  const currentColor = isNearHigh
    ? "text-emerald-400"
    : isNearLow
      ? "text-rose-400"
      : "text-amber-300";
  const pinGlow = isNearHigh
    ? "shadow-[0_0_6px_rgba(16,185,129,0.9)]"
    : isNearLow
      ? "shadow-[0_0_6px_rgba(244,63,94,0.85)]"
      : "shadow-[0_0_6px_rgba(252,211,77,0.8)]";

  return (
    <div className="rounded-lg border border-border/40 bg-card/40 px-3 py-2.5">
      {/* Row 1: sector + current price */}
      <div className="mb-2 flex items-baseline justify-between gap-2">
        <div className="flex min-w-0 items-baseline gap-1">
          <span className="truncate text-sm font-medium text-foreground">
            {getSectorLabel(sector.etf_symbol)}
          </span>
          {estimated && (
            <span className="shrink-0 text-[10px] text-muted-foreground">*</span>
          )}
          <span className="ml-1 shrink-0 font-mono text-[10px] text-muted-foreground">
            {positionPercent.toFixed(0)}%
          </span>
        </div>
        <span className={cn("shrink-0 font-mono text-base font-bold tabular-nums", currentColor)}>
          {formatPrice(current)}
        </span>
      </div>

      {/* Row 2: low — bar — high */}
      <div className="flex items-center gap-2">
        <span className="w-14 shrink-0 text-right font-mono text-[10px] tabular-nums text-muted-foreground">
          {formatPrice(low)}
        </span>
        <div className="relative h-2.5 flex-1 overflow-hidden rounded-full bg-slate-700/50">
          <div
            className="absolute inset-y-0 left-0 rounded-full bg-gradient-to-r from-slate-500/50 via-amber-500/50 to-emerald-500/80"
            style={{ width: `${positionPercent}%` }}
          />
          <div
            className={cn(
              "absolute top-1/2 h-4 w-0.5 -translate-y-1/2 bg-white",
              pinGlow,
            )}
            style={{ left: `calc(${positionPercent}% - 1px)` }}
          />
        </div>
        <span className="w-14 shrink-0 font-mono text-[10px] tabular-nums text-muted-foreground">
          {formatPrice(high)}
        </span>
      </div>
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
      <CardContent className="space-y-1.5">
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
