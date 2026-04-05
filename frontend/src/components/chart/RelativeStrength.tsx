import {
  Area,
  AreaChart,
  CartesianGrid,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import type { Sector } from "@/types";

interface RelativeStrengthProps {
  sectors: Sector[];
  loading: boolean;
}

export function RelativeStrength({ sectors, loading }: RelativeStrengthProps) {
  if (loading) {
    return (
      <Card>
        <CardHeader><CardTitle>Relative Strength vs S&P500</CardTitle></CardHeader>
        <CardContent><Skeleton className="h-64 w-full" /></CardContent>
      </Card>
    );
  }

  const data = sectors
    .filter((s) => s.relative_strength !== null)
    .sort((a, b) => (b.relative_strength ?? 0) - (a.relative_strength ?? 0))
    .map((s) => ({
      name: s.etf_symbol,
      rs: s.relative_strength ?? 0,
    }));

  return (
    <Card>
      <CardHeader><CardTitle>Relative Strength vs S&P500</CardTitle></CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={280}>
          <AreaChart data={data}>
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
                color: "var(--color-foreground)",
                fontSize: 12,
              }}
              formatter={(value: number) => [`${value.toFixed(2)}%`, "RS"]}
            />
            <ReferenceLine y={0} stroke="var(--color-muted-foreground)" strokeDasharray="3 3" />
            <defs>
              <linearGradient id="rsPositive" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="var(--color-bullish)" stopOpacity={0.4} />
                <stop offset="100%" stopColor="var(--color-bullish)" stopOpacity={0.05} />
              </linearGradient>
            </defs>
            <Area
              type="monotone"
              dataKey="rs"
              stroke="var(--color-bullish)"
              fill="url(#rsPositive)"
              strokeWidth={2}
            />
          </AreaChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
