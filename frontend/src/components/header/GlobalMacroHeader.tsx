import { RegimeBadge } from "./RegimeBadge";
import { TickerBar } from "./TickerBar";
import type { EconomicIndicator, MacroRegime, MarketIndex } from "@/types";

interface GlobalMacroHeaderProps {
  indices: MarketIndex[];
  indicators: EconomicIndicator[];
  regime: MacroRegime | null;
  loading: boolean;
  lastUpdated: string | null;
}

export function GlobalMacroHeader({
  indices,
  indicators,
  regime,
  loading,
  lastUpdated,
}: GlobalMacroHeaderProps) {
  return (
    <div className="border-b border-border bg-card px-4 py-3">
      <div className="flex flex-col gap-2 lg:flex-row lg:items-center lg:justify-between">
        <TickerBar indices={indices} indicators={indicators} loading={loading} />

        <div className="flex items-center gap-4">
          <RegimeBadge regime={regime} loading={loading} />
          {loading && (
            <span className="text-xs text-muted-foreground animate-pulse">
              AI 분석중...
            </span>
          )}
          {lastUpdated && !loading && (
            <span className="text-xs text-muted-foreground">
              갱신: {new Date(lastUpdated).toLocaleTimeString("ko-KR", { hour: "2-digit", minute: "2-digit" })}
            </span>
          )}
        </div>
      </div>
    </div>
  );
}
