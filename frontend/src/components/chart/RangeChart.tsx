import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { getSectorLabel } from "@/lib/i18n";
import { formatPrice } from "@/lib/utils";
import type { Sector } from "@/types";

interface RangeChartProps {
  sectors: Sector[];
  loading: boolean;
}

function BulletBar({ sector }: { sector: Sector }) {
  const current = sector.price;

  // Use real 52-week data if available, otherwise estimate from current price
  const hasRealData = (sector.week_52_low ?? 0) > 0 && (sector.week_52_high ?? 0) > 0;
  const low = hasRealData ? sector.week_52_low! : current * 0.8;
  const high = hasRealData ? sector.week_52_high! : current * 1.2;
  const estimated = !hasRealData;

  if (low >= high) {
    return (
      <div className="flex items-center gap-3 py-1.5">
        <span className="w-16 shrink-0 text-xs font-medium text-foreground">
          {getSectorLabel(sector.etf_symbol)}
        </span>
        <span className="text-xs text-bearish">데이터 오류</span>
      </div>
    );
  }

  const range = high - low;
  const position = Math.min(Math.max(((current - low) / range) * 100, 0), 100);
  const inRange = current >= low && current <= high;

  return (
    <div className="flex items-center gap-3 py-1.5">
      {/* Sector label */}
      <span className="w-16 shrink-0 text-xs font-medium text-foreground">
        {getSectorLabel(sector.etf_symbol)}
      </span>

      {/* Low price */}
      <span className="w-16 shrink-0 text-right font-mono text-[11px] text-muted-foreground">
        {formatPrice(low)}
      </span>

      {/* Range bar */}
      <div className="relative h-4 flex-1">
        {/* Full range background bar (low → high) */}
        <div
          className={`absolute top-1 h-2 rounded-full ${inRange ? "bg-emerald-500/25" : "bg-red-500/25"}`}
          style={{ left: "0%", width: "100%" }}
        />

        {/* Filled portion (low → current position) */}
        <div
          className={`absolute top-1 h-2 rounded-l-full ${inRange ? "bg-emerald-500/50" : "bg-red-500/50"}`}
          style={{ left: "0%", width: `${position}%` }}
        />

        {/* Current price marker */}
        <div
          className={`absolute top-0 h-4 w-0.5 rounded-full ${inRange ? "bg-emerald-400" : "bg-red-400"}`}
          style={{ left: `${position}%` }}
        />
      </div>

      {/* High price */}
      <span className="w-16 shrink-0 font-mono text-[11px] text-muted-foreground">
        {formatPrice(high)}
      </span>

      {/* Current price */}
      <span className={`w-16 shrink-0 text-right font-mono text-xs font-semibold ${inRange ? "text-emerald-400" : "text-red-400"}`}>
        {formatPrice(current)}
      </span>

      {/* Estimated indicator */}
      {estimated && (
        <span className="w-4 shrink-0 text-[9px] text-muted-foreground" title="추정 범위">*</span>
      )}
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

  return (
    <Card>
      <CardHeader>
        <CardTitle>52주 범위 차트</CardTitle>
        <p className="text-xs text-muted-foreground">
          최저가 — 현재가 위치 — 최고가 (녹색: 범위 내, 적색: 범위 이탈, *추정)
        </p>
      </CardHeader>
      <CardContent>
        {sectors.map((sector) => (
          <BulletBar key={sector.etf_symbol} sector={sector} />
        ))}
      </CardContent>
    </Card>
  );
}
