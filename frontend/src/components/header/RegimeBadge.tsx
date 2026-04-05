import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import type { MacroRegime, RegimeType } from "@/types";
import { REGIME_LABELS } from "@/types";

interface RegimeBadgeProps {
  regime: MacroRegime | null;
  loading: boolean;
}

export function RegimeBadge({ regime, loading }: RegimeBadgeProps) {
  if (loading) {
    return <Skeleton className="h-6 w-40" />;
  }

  if (!regime) {
    return (
      <Badge variant="default">
        국면 데이터 없음
      </Badge>
    );
  }

  const regimeType = regime.regime as RegimeType;
  const confidence = regime.regime_probabilities[regimeType];
  const confidencePercent = confidence ? `${(confidence * 100).toFixed(0)}%` : "";

  return (
    <div className="flex items-center gap-2">
      <span className="text-xs text-muted-foreground">현재 국면:</span>
      <Badge variant={regimeType}>
        {REGIME_LABELS[regimeType]} {confidencePercent && `(${confidencePercent})`}
      </Badge>
    </div>
  );
}
