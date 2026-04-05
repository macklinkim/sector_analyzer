import { useState } from "react";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import type { RotationSignal } from "@/types";

interface EventMarkerProps {
  signals: RotationSignal[];
}

export function EventMarker({ signals }: EventMarkerProps) {
  const [expanded, setExpanded] = useState<string | null>(null);

  if (signals.length === 0) return null;

  return (
    <div className="space-y-1">
      <h4 className="text-xs font-semibold text-muted-foreground">AI Event Signals</h4>
      <div className="flex flex-wrap gap-1.5">
        {signals.slice(0, 8).map((signal, i) => {
          const key = `${signal.signal_type}-${signal.to_sector ?? signal.from_sector}-${i}`;
          const isExpanded = expanded === key;

          return (
            <button
              key={key}
              onClick={() => setExpanded(isExpanded ? null : key)}
              className={cn(
                "rounded-md border border-border px-2 py-1 text-xs transition-colors hover:bg-muted/50",
                isExpanded && "bg-muted/70",
              )}
            >
              <div className="flex items-center gap-1.5">
                <Badge
                  variant={signal.signal_type.includes("in") ? "bullish" : "bearish"}
                  className="text-[9px] px-1.5 py-0"
                >
                  {signal.signal_type === "rotate_in" ? "IN" : signal.signal_type === "rotate_out" ? "OUT" : "SHIFT"}
                </Badge>
                <span className="text-foreground">
                  {signal.to_sector ?? signal.from_sector ?? "Market"}
                </span>
              </div>
              {isExpanded && (
                <p className="mt-1 text-left text-[10px] text-muted-foreground">
                  {signal.reasoning}
                </p>
              )}
            </button>
          );
        })}
      </div>
    </div>
  );
}
