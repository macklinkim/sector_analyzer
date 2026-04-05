import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { getSectorLabel } from "@/lib/i18n";
import { cn } from "@/lib/utils";
import { formatPrice } from "@/lib/utils";
import type { Sector } from "@/types";

interface RangeChartProps {
  sectors: Sector[];
  loading: boolean;
}

function BulletBar({ sector }: { sector: Sector }) {
  const low52 = sector.price * 0.75;
  const high52 = sector.price * 1.25;
  const range = high52 - low52;
  const position = range > 0 ? ((sector.price - low52) / range) * 100 : 50;

  return (
    <div className="flex items-center gap-3 py-1">
      <span className="w-14 shrink-0 text-xs text-muted-foreground">
        {getSectorLabel(sector.etf_symbol)}
      </span>
      <span className="w-14 shrink-0 text-right font-mono text-xs text-muted-foreground">
        {formatPrice(low52)}
      </span>
      <div className="relative h-3 flex-1 rounded-full bg-muted/50">
        <div
          className={cn(
            "absolute top-0 h-3 rounded-full",
            sector.change_percent >= 0 ? "bg-bullish/30" : "bg-bearish/30",
          )}
          style={{ width: `${Math.min(position, 100)}%` }}
        />
        <div
          className="absolute top-[-2px] h-[18px] w-[3px] rounded-full bg-foreground"
          style={{ left: `${Math.min(Math.max(position, 0), 100)}%` }}
        />
      </div>
      <span className="w-14 shrink-0 font-mono text-xs text-muted-foreground">
        {formatPrice(high52)}
      </span>
      <span className="w-16 shrink-0 text-right font-mono text-xs font-medium text-foreground">
        {formatPrice(sector.price)}
      </span>
    </div>
  );
}

export function RangeChart({ sectors, loading }: RangeChartProps) {
  if (loading) {
    return (
      <Card>
        <CardHeader><CardTitle>52-Week Range</CardTitle></CardHeader>
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
      <CardHeader><CardTitle>52-Week Range</CardTitle></CardHeader>
      <CardContent>
        {sectors.map((sector) => (
          <BulletBar key={sector.etf_symbol} sector={sector} />
        ))}
      </CardContent>
    </Card>
  );
}
