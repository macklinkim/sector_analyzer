import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import { getSectorLabel } from "@/lib/i18n";
import type { RotationSignal } from "@/types";

interface EventMarkerProps {
  signals: RotationSignal[];
}

const GRADE_CONFIG = {
  MAJOR: { label: "MAJOR", icon: "🔴", border: "border-red-500/40", bg: "bg-red-500/10", text: "text-red-400" },
  ALERT: { label: "ALERT", icon: "🟡", border: "border-amber-500/40", bg: "bg-amber-500/10", text: "text-amber-400" },
  WATCH: { label: "WATCH", icon: "🔵", border: "border-blue-500/30", bg: "bg-blue-500/10", text: "text-blue-400" },
} as const;

function ConfidenceBar({ score }: { score: number }) {
  const pct = Math.min(score * 100, 100);
  const color = score >= 0.7 ? "bg-red-500" : score >= 0.5 ? "bg-amber-500" : "bg-blue-500";
  return (
    <div className="flex items-center gap-2">
      <span className="text-[10px] text-muted-foreground">확신도</span>
      <div className="h-1.5 w-14 overflow-hidden rounded-full bg-muted">
        <div className={cn("h-full rounded-full", color)} style={{ width: `${pct}%` }} />
      </div>
      <span className="text-xs font-mono font-bold text-muted-foreground">
        {(score * 100).toFixed(0)}%
      </span>
    </div>
  );
}

export function EventMarker({ signals }: EventMarkerProps) {
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
            {signals.length}건
          </span>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-2">
        {topSignals.map((signal, i) => {
          const grade = GRADE_CONFIG[signal.signal_grade as keyof typeof GRADE_CONFIG] ?? GRADE_CONFIG.WATCH;
          const sector = signal.to_sector ?? signal.from_sector ?? "Market";
          const typeLabel =
            signal.signal_type === "rotate_in" ? "ROTATE IN" :
            signal.signal_type === "rotate_out" ? "ROTATE OUT" : "REGIME SHIFT";

          return (
            <div
              key={`${signal.signal_type}-${sector}-${i}`}
              className={cn(
                "w-full rounded-lg border p-3 text-left",
                grade.border,
                grade.bg,
              )}
            >
              <div className="flex items-start gap-4">
                {/* Left: AI reasoning (always visible) */}
                <p className="w-1/3 shrink-0 text-xs leading-relaxed text-muted-foreground">
                  {signal.reasoning}
                </p>

                {/* Right: existing first-row content (icon + sector info + date) */}
                <div className="flex flex-1 items-center gap-3 min-w-0">
                  <span className="text-lg">{grade.icon}</span>
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-2">
                      <span className={cn("rounded px-1.5 py-0.5 text-[10px] font-bold", grade.bg, grade.text)}>
                        {grade.label}
                      </span>
                      <Badge
                        variant={signal.signal_type.includes("in") ? "bullish" : "bearish"}
                        className="text-[10px] px-1.5 py-0"
                      >
                        {typeLabel}
                      </Badge>
                      <span className="text-sm font-semibold text-foreground truncate">
                        {sector}
                        <span className="ml-1 text-xs font-normal text-muted-foreground">
                          {getSectorLabel(sector)}
                        </span>
                      </span>
                    </div>
                    <div className="mt-1 flex items-center gap-3">
                      <ConfidenceBar score={signal.confidence_score ?? 0.5} />
                      {signal.macro_environment && (
                        <span className="rounded bg-muted px-1.5 py-0.5 text-[10px] text-muted-foreground">
                          {signal.macro_environment}
                        </span>
                      )}
                    </div>
                  </div>
                  <span className="text-xs text-muted-foreground shrink-0">
                    {new Date(signal.detected_at).toLocaleDateString("ko-KR", { month: "short", day: "numeric" })}
                  </span>
                </div>
              </div>
            </div>
          );
        })}
      </CardContent>
    </Card>
  );
}
