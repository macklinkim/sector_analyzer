import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  LabelList,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { getSectorLabel } from "@/lib/i18n";
import type { Sector } from "@/types";

interface RelativeStrengthProps {
  sectors: Sector[];
  loading: boolean;
}

export function RelativeStrength({ sectors, loading }: RelativeStrengthProps) {
  if (loading) {
    return (
      <Card>
        <CardHeader><CardTitle>상대 강도 vs S&P500</CardTitle></CardHeader>
        <CardContent><Skeleton className="h-64 w-full" /></CardContent>
      </Card>
    );
  }

  // Deduplicate by etf_symbol (keep first/latest), filter null/zero, sort descending
  const seen = new Set<string>();
  const data = sectors
    .filter((s) => {
      if (s.relative_strength === null || s.relative_strength === 0) return false;
      if (seen.has(s.etf_symbol)) return false;
      seen.add(s.etf_symbol);
      return true;
    })
    .sort((a, b) => (b.relative_strength ?? 0) - (a.relative_strength ?? 0))
    .map((s) => ({
      name: getSectorLabel(s.etf_symbol),
      symbol: s.etf_symbol,
      rs: Number((s.relative_strength ?? 0).toFixed(2)),
    }));

  if (data.length === 0) {
    return (
      <Card>
        <CardHeader><CardTitle>상대 강도 vs S&P500</CardTitle></CardHeader>
        <CardContent>
          <p className="py-8 text-center text-sm text-muted-foreground">
            상대 강도 데이터가 아직 없습니다
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>상대 강도 vs S&P500</CardTitle>
        <p className="text-xs text-muted-foreground">
          1개월 수익률 - SPY 수익률 (녹색: 초과, 적색: 하회)
        </p>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={data} barSize={28} barCategoryGap="20%">
            <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" vertical={false} />
            <XAxis
              dataKey="name"
              tick={{ fill: "var(--color-muted-foreground)", fontSize: 10 }}
              axisLine={{ stroke: "var(--color-border)" }}
              tickLine={false}
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
              itemStyle={{ color: "var(--color-foreground)" }}
              formatter={(value) => [`RS : ${(value as number).toFixed(2)}%`]}
              labelFormatter={(label) => `${label}`}
            />
            <ReferenceLine y={0} stroke="var(--color-muted-foreground)" strokeWidth={1.5} />
            <Bar dataKey="rs" radius={[4, 4, 0, 0]}>
              <LabelList
                dataKey="rs"
                position="top"
                formatter={(v: unknown) => { const n = Number(v); return `${n > 0 ? "+" : ""}${n.toFixed(1)}%`; }}
                style={{ fontSize: 10, fontWeight: 600, fill: "hsl(var(--muted-foreground))" }}
              />
              {data.map((entry) => (
                <Cell
                  key={entry.symbol}
                  fill={entry.rs >= 0 ? "#22c55e" : "#ef4444"}
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
