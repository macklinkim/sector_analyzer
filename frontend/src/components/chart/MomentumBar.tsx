import { useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { getSectorLabel } from "@/lib/i18n";
import type { Sector } from "@/types";

interface MomentumBarProps {
  sectors: Sector[];
  loading: boolean;
}

const TIMEFRAMES = [
  { key: "1D", color: "#94a3b8", label: "1D" },
  { key: "1W", color: "#60a5fa", label: "1W" },
  { key: "1M", color: "#22c55e", label: "1M" },
  { key: "3M", color: "#f59e0b", label: "3M" },
  { key: "6M", color: "#f97316", label: "6M" },
  { key: "1Y", color: "#a78bfa", label: "1Y" },
] as const;

type TimeframeKey = (typeof TIMEFRAMES)[number]["key"];

export function MomentumBar({ sectors, loading }: MomentumBarProps) {
  const [active, setActive] = useState<Set<TimeframeKey>>(
    new Set(["1W", "1M", "3M", "1Y"])
  );

  if (loading) {
    return (
      <Card>
        <CardHeader><CardTitle>Sector Momentum</CardTitle></CardHeader>
        <CardContent><Skeleton className="h-64 w-full" /></CardContent>
      </Card>
    );
  }

  const toggle = (key: TimeframeKey) => {
    setActive((prev) => {
      const next = new Set(prev);
      if (next.has(key)) {
        if (next.size > 1) next.delete(key);
      } else {
        next.add(key);
      }
      return next;
    });
  };

  const data = sectors.map((s) => ({
    name: getSectorLabel(s.etf_symbol),
    "1D": s.change_percent ?? 0,
    "1W": s.momentum_1w ?? 0,
    "1M": s.momentum_1m ?? 0,
    "3M": s.momentum_3m ?? 0,
    "6M": s.momentum_6m ?? 0,
    "1Y": s.momentum_1y ?? 0,
  }));

  const activeFrames = TIMEFRAMES.filter((t) => active.has(t.key));

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>섹터 모멘텀</CardTitle>
          <div className="flex gap-1">
            {TIMEFRAMES.map((t) => (
              <button
                key={t.key}
                onClick={() => toggle(t.key)}
                className={`rounded px-2 py-0.5 text-[10px] font-semibold transition-colors ${
                  active.has(t.key)
                    ? "text-white"
                    : "bg-muted/40 text-muted-foreground hover:bg-muted"
                }`}
                style={active.has(t.key) ? { backgroundColor: t.color } : undefined}
              >
                {t.label}
              </button>
            ))}
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={data} barGap={1} barCategoryGap="15%">
            <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
            <XAxis
              dataKey="name"
              tick={{ fill: "var(--color-muted-foreground)", fontSize: 10 }}
              axisLine={{ stroke: "var(--color-border)" }}
            />
            <YAxis
              tick={{ fill: "var(--color-muted-foreground)", fontSize: 10 }}
              axisLine={{ stroke: "var(--color-border)" }}
              tickFormatter={(v: number) => `${v}%`}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: "var(--color-card)",
                border: "1px solid var(--color-border)",
                borderRadius: 8,
                fontSize: 12,
              }}
              labelStyle={{ color: "var(--color-foreground)", fontWeight: 600 }}
              formatter={(value, name, props) => [
                `${(value as number).toFixed(2)}%`,
                <span style={{ color: props.color }}>{String(name)}</span>,
              ]}
              itemSorter={(item) => {
                const order: Record<string, number> = { "1D": 0, "1W": 1, "1M": 2, "3M": 3, "6M": 4, "1Y": 5 };
                return order[item.dataKey as string] ?? 99;
              }}
            />
            <Legend
              content={() => (
                <ul className="flex justify-center gap-4 pt-1 text-[11px] text-muted-foreground">
                  {activeFrames.map(({ key, color }) => (
                    <li key={key} className="flex items-center gap-1">
                      <span className="inline-block h-2.5 w-2.5 rounded-sm" style={{ backgroundColor: color }} />
                      {key}
                    </li>
                  ))}
                </ul>
              )}
            />
            {activeFrames.map((t) => (
              <Bar key={t.key} dataKey={t.key} fill={t.color} radius={[2, 2, 0, 0]} />
            ))}
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
