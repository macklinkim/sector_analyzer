import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import type { EconomicIndicator } from "@/types";
import { formatPrice } from "@/lib/utils";
import { cn } from "@/lib/utils";

interface EconomicCalendarProps {
  indicators: EconomicIndicator[];
  loading: boolean;
}

function getDirectionIcon(direction: string): string {
  if (direction === "up") return "▲";
  if (direction === "down") return "▼";
  return "—";
}

function getDirectionColor(direction: string): string {
  if (direction === "up") return "text-bullish";
  if (direction === "down") return "text-bearish";
  return "text-muted-foreground";
}

export function EconomicCalendar({ indicators, loading }: EconomicCalendarProps) {
  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Economic Calendar</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} className="h-10 w-full" />
          ))}
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Economic Calendar</CardTitle>
      </CardHeader>
      <CardContent>
        {indicators.length === 0 ? (
          <p className="py-4 text-center text-sm text-muted-foreground">
            경제 지표 데이터 없음
          </p>
        ) : (
          <div className="space-y-1">
            {indicators.map((ind) => (
              <div
                key={ind.indicator_name}
                className="flex items-center justify-between rounded-lg px-3 py-2 text-sm hover:bg-muted/30"
              >
                <div className="flex items-center gap-2">
                  <span
                    className={cn("text-xs", getDirectionColor(ind.change_direction))}
                  >
                    {getDirectionIcon(ind.change_direction)}
                  </span>
                  <span className="font-medium text-foreground">
                    {ind.indicator_name}
                  </span>
                </div>
                <div className="flex items-center gap-3">
                  <span className="font-mono text-xs text-foreground">
                    {formatPrice(ind.value)}
                  </span>
                  {ind.previous_value !== null && (
                    <span className="font-mono text-xs text-muted-foreground">
                      (prev: {formatPrice(ind.previous_value)})
                    </span>
                  )}
                  <span className="text-xs text-muted-foreground">
                    {new Date(ind.reported_at).toLocaleDateString("ko-KR", {
                      month: "short",
                      day: "numeric",
                    })}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
