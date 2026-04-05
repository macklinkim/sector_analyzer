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

export function MomentumBar({ sectors, loading }: MomentumBarProps) {
  if (loading) {
    return (
      <Card>
        <CardHeader><CardTitle>Sector Momentum</CardTitle></CardHeader>
        <CardContent><Skeleton className="h-64 w-full" /></CardContent>
      </Card>
    );
  }

  const data = sectors.map((s) => ({
    name: getSectorLabel(s.etf_symbol),
    "1W": s.momentum_1w ?? 0,
    "1M": s.momentum_1m ?? 0,
    "3M": s.momentum_3m ?? 0,
    "1Y": s.momentum_1y ?? 0,
  }));

  return (
    <Card>
      <CardHeader><CardTitle>섹터 모멘텀 (1W / 1M / 3M / 1Y)</CardTitle></CardHeader>
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
                color: "var(--color-foreground)",
                fontSize: 12,
              }}
              formatter={(value) => [`${(value as number).toFixed(2)}%`]}
            />
            <Legend wrapperStyle={{ fontSize: 11, color: "var(--color-muted-foreground)" }} />
            <Bar dataKey="1W" fill="#60a5fa" radius={[2, 2, 0, 0]} />
            <Bar dataKey="1M" fill="#22c55e" radius={[2, 2, 0, 0]} />
            <Bar dataKey="3M" fill="#f59e0b" radius={[2, 2, 0, 0]} />
            <Bar dataKey="1Y" fill="#a78bfa" radius={[2, 2, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
