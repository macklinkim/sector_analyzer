import { Skeleton } from "@/components/ui/skeleton";
import { getIndexLabel } from "@/lib/i18n";
import { formatPercent, formatPrice, getChangeColor } from "@/lib/utils";
import type { EconomicIndicator, MarketIndex } from "@/types";

interface TickerBarProps {
  indices: MarketIndex[];
  indicators: EconomicIndicator[];
  loading: boolean;
}

const INDICATOR_DISPLAY: Record<string, { label: string; prefix?: string }> = {
  US10Y: { label: "US10Y" },
  DXY: { label: "DXY" },
  WTI: { label: "WTI", prefix: "$" },
  GOLD: { label: "Gold", prefix: "$" },
};

export function TickerBar({ indices, indicators, loading }: TickerBarProps) {
  if (loading) {
    return (
      <div className="flex gap-6">
        {Array.from({ length: 8 }).map((_, i) => (
          <Skeleton key={i} className="h-5 w-32" />
        ))}
      </div>
    );
  }

  return (
    <div className="flex flex-wrap items-center gap-x-5 gap-y-1">
      {/* Indices with price + change */}
      {indices.map((idx) => (
        <div key={idx.symbol} className="flex items-center gap-1.5 text-sm">
          <span className="text-muted-foreground">{getIndexLabel(idx.name)}</span>
          <span className="font-medium text-foreground">{formatPrice(idx.price)}</span>
          <span className={getChangeColor(idx.change_percent)}>
            {formatPercent(idx.change_percent)}
          </span>
        </div>
      ))}

      {/* Divider */}
      {indices.length > 0 && indicators.length > 0 && (
        <div className="h-4 w-px bg-border" />
      )}

      {/* Economic Indicators */}
      {indicators.map((ind) => {
        const display = INDICATOR_DISPLAY[ind.indicator_name];
        if (!display) return null;
        return (
          <div key={ind.indicator_name} className="flex items-center gap-1.5 text-sm">
            <span className="text-muted-foreground">{display.label}</span>
            <span className="font-medium text-foreground">
              {display.prefix ?? ""}{formatPrice(ind.value)}
            </span>
          </div>
        );
      })}
    </div>
  );
}
