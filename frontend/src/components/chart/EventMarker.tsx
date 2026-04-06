import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import type { RotationSignal } from "@/types";

interface EventMarkerProps {
  signals: RotationSignal[];
}

function SignalIcon({ type }: { type: string }) {
  if (type === "rotate_in") return <span className="text-lg">📈</span>;
  if (type === "rotate_out") return <span className="text-lg">📉</span>;
  return <span className="text-lg">🔄</span>;
}

function ScoreBar({ score }: { score: number }) {
  const pct = Math.min(Math.abs(score) * 100, 100);
  const isPositive = score >= 0;
  return (
    <div className="flex items-center gap-2">
      <div className="h-1.5 w-16 overflow-hidden rounded-full bg-muted">
        <div
          className={cn(
            "h-full rounded-full transition-all",
            isPositive ? "bg-emerald-500" : "bg-red-500",
          )}
          style={{ width: `${pct}%` }}
        />
      </div>
      <span className={cn("text-xs font-mono font-bold", isPositive ? "text-emerald-400" : "text-red-400")}>
        {score > 0 ? "+" : ""}{score.toFixed(2)}
      </span>
    </div>
  );
}

export function EventMarker({ signals }: EventMarkerProps) {
  const [expandedIdx, setExpandedIdx] = useState<number | null>(null);

  if (signals.length === 0) return null;

  const topSignals = signals.slice(0, 6);

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="flex items-center gap-2">
          <span className="relative flex h-2.5 w-2.5">
            <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-amber-400 opacity-75" />
            <span className="relative inline-flex h-2.5 w-2.5 rounded-full bg-amber-500" />
          </span>
          AI Rotation Signals
          <span className="ml-auto rounded-md border border-border px-1.5 py-0.5 text-[10px] font-normal text-muted-foreground">
            {signals.length}건 감지
          </span>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-2">
        {topSignals.map((signal, i) => {
          const isExpanded = expandedIdx === i;
          const isBullish = signal.signal_type.includes("in");
          const sector = signal.to_sector ?? signal.from_sector ?? "Market";
          const label =
            signal.signal_type === "rotate_in" ? "ROTATE IN" :
            signal.signal_type === "rotate_out" ? "ROTATE OUT" : "REGIME SHIFT";

          return (
            <button
              key={`${signal.signal_type}-${sector}-${i}`}
              onClick={() => setExpandedIdx(isExpanded ? null : i)}
              className={cn(
                "w-full rounded-lg border p-3 text-left transition-all",
                isBullish
                  ? "border-emerald-500/30 hover:border-emerald-500/60 hover:bg-emerald-500/5"
                  : "border-red-500/30 hover:border-red-500/60 hover:bg-red-500/5",
                isExpanded && (isBullish ? "bg-emerald-500/10 border-emerald-500/60" : "bg-red-500/10 border-red-500/60"),
              )}
            >
              <div className="flex items-center gap-3">
                <SignalIcon type={signal.signal_type} />
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2">
                    <Badge
                      variant={isBullish ? "bullish" : "bearish"}
                      className="text-[10px] px-1.5 py-0"
                    >
                      {label}
                    </Badge>
                    <span className="text-sm font-semibold text-foreground truncate">
                      {sector}
                    </span>
                  </div>
                  <div className="mt-1">
                    <ScoreBar score={signal.final_score} />
                  </div>
                </div>
                <span className="text-xs text-muted-foreground shrink-0">
                  {new Date(signal.detected_at).toLocaleDateString("ko-KR", { month: "short", day: "numeric" })}
                </span>
              </div>
              {isExpanded && (
                <p className="mt-2 border-t border-border/50 pt-2 text-xs leading-relaxed text-muted-foreground">
                  {signal.reasoning}
                </p>
              )}
            </button>
          );
        })}
      </CardContent>
    </Card>
  );
}
