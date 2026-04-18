import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { getSectorLabel } from "@/lib/i18n";
import { cn } from "@/lib/utils";
import { getChangeColor } from "@/lib/utils";
import type { SectorScoreboard } from "@/types";

interface AiScreenerTableProps {
  scoreboards: SectorScoreboard[];
  loading: boolean;
  selectedSector?: string | null;
  onSectorClick?: (sectorName: string) => void;
}

function getRecommendationVariant(rec: string): "bullish" | "bearish" | "default" {
  if (rec === "overweight") return "bullish";
  if (rec === "underweight") return "bearish";
  return "default";
}

export function AiScreenerTable({ scoreboards, loading, selectedSector, onSectorClick }: AiScreenerTableProps) {
  if (loading) {
    return (
      <Card>
        <CardHeader><CardTitle>AI Sector Screener</CardTitle></CardHeader>
        <CardContent className="space-y-2">
          {Array.from({ length: 5 }).map((_, i) => (
            <Skeleton key={i} className="h-8 w-full" />
          ))}
        </CardContent>
      </Card>
    );
  }

  const sorted = [...scoreboards].sort((a, b) => a.rank - b.rank);

  return (
    <Card>
      <CardHeader><CardTitle>AI Sector Screener</CardTitle></CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border text-xs text-muted-foreground">
                <th className="px-2 py-2 text-left">Rank</th>
                <th className="px-2 py-2 text-left">Sector</th>
                <th className="px-2 py-2 text-right">AI Score</th>
                <th className="px-2 py-2 text-right">Momentum</th>
                <th className="px-2 py-2 text-center">Signal</th>
              </tr>
            </thead>
            <tbody>
              {sorted.map((sb) => (
                <tr
                  key={sb.etf_symbol}
                  className={cn(
                    "border-b border-border/50 transition-colors hover:bg-muted/20 cursor-pointer",
                    selectedSector === sb.sector_name && "bg-muted/30 ring-1 ring-inset ring-primary/30"
                  )}
                  onClick={() => onSectorClick?.(sb.sector_name)}
                >
                  <td className="px-2 py-2 font-mono text-xs text-muted-foreground">
                    #{sb.rank}
                  </td>
                  <td className="px-2 py-2 font-medium text-foreground">
                    {getSectorLabel(sb.sector_name)}
                  </td>
                  <td className={cn("px-2 py-2 text-right font-mono font-bold", getChangeColor(sb.final_score))}>
                    {sb.final_score.toFixed(2)}
                  </td>
                  <td className={cn("px-2 py-2 text-right font-mono text-xs", getChangeColor(sb.momentum_score))}>
                    {sb.momentum_score.toFixed(2)}
                  </td>
                  <td className="px-2 py-2 text-center">
                    <Badge variant={getRecommendationVariant(sb.recommendation)}>
                      {sb.recommendation}
                    </Badge>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {sorted.length === 0 && (
          <p className="py-8 text-center text-sm text-muted-foreground">
            스크리너 데이터 없음
          </p>
        )}
      </CardContent>
    </Card>
  );
}
