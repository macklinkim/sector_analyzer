import { Line, LineChart, ResponsiveContainer, XAxis, Tooltip } from "recharts";
import { getSectorLabel } from "@/lib/i18n";
import { cn } from "@/lib/utils";
import { formatPercent, getChangeColor } from "@/lib/utils";
import type { Sector } from "@/types";

interface SectorSparklineProps {
  sectors: Sector[];
  selectedSector: string | null;
  onSectorClick: (sectorName: string) => void;
}

function generateSparklineData(positive: boolean) {
  const today = new Date();
  return Array.from({ length: 30 }, (_, i) => {
    const d = new Date(today);
    d.setDate(d.getDate() - (29 - i));
    return {
      date: `${d.getMonth() + 1}/${d.getDate()}`,
      value: 50 + Math.sin(i / 3) * 10 + (positive ? i * 0.5 : -i * 0.5) + Math.random() * 5,
    };
  });
}

function SparklineChart({ positive }: { positive: boolean }) {
  const data = generateSparklineData(positive);
  const color = positive ? "var(--color-bullish)" : "var(--color-bearish)";

  return (
    <ResponsiveContainer width="100%" height={40}>
      <LineChart data={data}>
        <XAxis
          dataKey="date"
          tick={{ fill: "var(--color-muted-foreground)", fontSize: 8 }}
          axisLine={false}
          tickLine={false}
          interval={6}
        />
        <Tooltip
          contentStyle={{
            backgroundColor: "var(--color-card)",
            border: "1px solid var(--color-border)",
            borderRadius: 6,
            fontSize: 11,
            color: "var(--color-foreground)",
          }}
          formatter={(value) => [(value as number).toFixed(1), "가격"]}
        />
        <Line
          type="monotone"
          dataKey="value"
          stroke={color}
          strokeWidth={1.5}
          dot={false}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}

export function SectorSparkline({ sectors, selectedSector, onSectorClick }: SectorSparklineProps) {
  return (
    <div className="space-y-2">
      {sectors.map((sector) => (
        <button
          key={sector.etf_symbol}
          onClick={() => onSectorClick(sector.name)}
          className={cn(
            "flex w-full flex-col gap-1 rounded-lg px-3 py-2 text-left transition-colors hover:bg-muted/50",
            selectedSector === sector.name && "bg-muted/70",
          )}
        >
          <div className="flex w-full items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="w-10 font-mono text-xs text-muted-foreground">
                {sector.etf_symbol}
              </span>
              <span className="text-sm font-medium text-foreground">
                {getSectorLabel(sector.etf_symbol) !== sector.etf_symbol
                  ? getSectorLabel(sector.etf_symbol)
                  : sector.name}
              </span>
            </div>
            <span className={cn("font-mono text-xs", getChangeColor(sector.change_percent))}>
              {formatPercent(sector.change_percent)}
            </span>
          </div>
          <div className="w-full">
            <SparklineChart positive={sector.change_percent >= 0} />
          </div>
        </button>
      ))}
    </div>
  );
}
