import { Line, LineChart, ResponsiveContainer } from "recharts";
import { cn } from "@/lib/utils";
import { formatPercent, getChangeColor } from "@/lib/utils";
import type { Sector } from "@/types";

interface SectorSparklineProps {
  sectors: Sector[];
  selectedSector: string | null;
  onSectorClick: (sectorName: string) => void;
}

function MiniSparkline({ positive }: { positive: boolean }) {
  const data = Array.from({ length: 30 }, (_, i) => ({
    value: 50 + Math.sin(i / 3) * 10 + (positive ? i * 0.5 : -i * 0.5) + Math.random() * 5,
  }));

  return (
    <ResponsiveContainer width={80} height={24}>
      <LineChart data={data}>
        <Line
          type="monotone"
          dataKey="value"
          stroke={positive ? "var(--color-bullish)" : "var(--color-bearish)"}
          strokeWidth={1.5}
          dot={false}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}

export function SectorSparkline({ sectors, selectedSector, onSectorClick }: SectorSparklineProps) {
  return (
    <div className="space-y-1">
      {sectors.map((sector) => (
        <button
          key={sector.etf_symbol}
          onClick={() => onSectorClick(sector.name)}
          className={cn(
            "flex w-full items-center justify-between rounded-lg px-3 py-2 text-left text-sm transition-colors hover:bg-muted/50",
            selectedSector === sector.name && "bg-muted/70",
          )}
        >
          <div className="flex items-center gap-2">
            <span className="w-10 font-mono text-xs text-muted-foreground">
              {sector.etf_symbol}
            </span>
            <span className="font-medium text-foreground">{sector.name}</span>
          </div>
          <div className="flex items-center gap-3">
            <MiniSparkline positive={sector.change_percent >= 0} />
            <span className={cn("w-16 text-right font-mono text-xs", getChangeColor(sector.change_percent))}>
              {formatPercent(sector.change_percent)}
            </span>
          </div>
        </button>
      ))}
    </div>
  );
}
