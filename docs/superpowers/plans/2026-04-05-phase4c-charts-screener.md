# Phase 4c: Area D (Charts & AI Screener)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 대시보드 Area D — Multi-Chart Grid(MomentumBar, RelativeStrength, RangeChart), EventMarker 오버레이, AI Screener 테이블 구현. Phase 4a placeholder를 실제 컴포넌트로 교체하여 프론트엔드 완성.

**Architecture:** Multi-Chart Grid 2분할 컨테이너 안에 Recharts 기반 차트 컴포넌트 배치. 분석 데이터(scoreboards, signals)는 useAnalysisData 커스텀 훅으로 fetch. AiScreenerTable은 SectorScoreboard 데이터를 테이블로 렌더링.

**Tech Stack:** React 19, Recharts (BarChart, AreaChart, custom), Tailwind CSS v4, shadcn/ui

**Spec:** `docs/superpowers/specs/2026-04-05-market-insights-dashboard-design.md` (Section 5.2 Area D, 5.3)
**Frontend Rules:** `.claude/rules/frontend.md`

---

## File Map

| Action | Path | Responsibility |
|--------|------|----------------|
| Create | `frontend/src/hooks/useAnalysisData.ts` | 분석 결과 (scoreboards, signals, report) fetch 훅 |
| Create | `frontend/src/components/chart/MomentumBar.tsx` | 섹터별 1D/1W/1M Grouped Bar Chart |
| Create | `frontend/src/components/chart/RelativeStrength.tsx` | S&P500 기준 상대강도 Baseline Area Chart |
| Create | `frontend/src/components/chart/RangeChart.tsx` | 52주 Range Bullet Chart |
| Create | `frontend/src/components/chart/EventMarker.tsx` | AI 이벤트 마커 (뉴스/지표 시점 표시) |
| Create | `frontend/src/components/chart/MultiChartGrid.tsx` | 2분할 차트 컨테이너 |
| Create | `frontend/src/components/screener/AiScreenerTable.tsx` | AI Top Picks 스크리너 테이블 |
| Modify | `frontend/src/App.tsx` | Area D placeholder → 실제 컴포넌트 교체 |

---

## Task 1: useAnalysisData 커스텀 훅

**Files:**
- Create: `frontend/src/hooks/useAnalysisData.ts`

- [ ] **Step 1: useAnalysisData 훅 작성**

```ts
// frontend/src/hooks/useAnalysisData.ts
import { useCallback, useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { MarketReport, RotationSignal, SectorScoreboard } from "@/types";

interface AnalysisData {
  scoreboards: SectorScoreboard[];
  signals: RotationSignal[];
  report: MarketReport | null;
  loading: boolean;
  error: string | null;
}

export function useAnalysisData(): AnalysisData & { refresh: () => void } {
  const [data, setData] = useState<AnalysisData>({
    scoreboards: [],
    signals: [],
    report: null,
    loading: true,
    error: null,
  });

  const fetchData = useCallback(async () => {
    setData((prev) => ({ ...prev, loading: true, error: null }));
    try {
      const [scoreboards, signals, report] = await Promise.all([
        api.getScoreboards(),
        api.getSignals(),
        api.getReport().catch(() => null),
      ]);
      setData({ scoreboards, signals, report, loading: false, error: null });
    } catch (err) {
      setData((prev) => ({
        ...prev,
        loading: false,
        error: err instanceof Error ? err.message : "Failed to fetch analysis",
      }));
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return { ...data, refresh: fetchData };
}
```

- [ ] **Step 2: tsc 확인**

```bash
cd frontend && npx tsc --noEmit
```

- [ ] **Step 3: 커밋**

```bash
git add frontend/src/hooks/useAnalysisData.ts
git commit -m "feat: add useAnalysisData hook for scoreboards, signals, report"
```

---

## Task 2: MomentumBar (Grouped Bar Chart)

**Files:**
- Create: `frontend/src/components/chart/MomentumBar.tsx`

- [ ] **Step 1: 디렉토리 생성**

```bash
mkdir -p frontend/src/components/chart
```

- [ ] **Step 2: MomentumBar 컴포넌트 작성**

```tsx
// frontend/src/components/chart/MomentumBar.tsx
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
    name: s.etf_symbol,
    "1W": s.momentum_1w ?? 0,
    "1M": s.momentum_1m ?? 0,
    "3M": s.momentum_3m ?? 0,
  }));

  return (
    <Card>
      <CardHeader><CardTitle>Sector Momentum (1W / 1M / 3M)</CardTitle></CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={280}>
          <BarChart data={data} barGap={1} barCategoryGap="20%">
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
              formatter={(value: number) => [`${value.toFixed(2)}%`]}
            />
            <Legend wrapperStyle={{ fontSize: 11, color: "var(--color-muted-foreground)" }} />
            <Bar dataKey="1W" fill="#60a5fa" radius={[2, 2, 0, 0]} />
            <Bar dataKey="1M" fill="#22c55e" radius={[2, 2, 0, 0]} />
            <Bar dataKey="3M" fill="#f59e0b" radius={[2, 2, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
```

- [ ] **Step 3: tsc 확인**

```bash
cd frontend && npx tsc --noEmit
```

- [ ] **Step 4: 커밋**

```bash
git add frontend/src/components/chart/MomentumBar.tsx
git commit -m "feat: add MomentumBar grouped bar chart (1W/1M/3M)"
```

---

## Task 3: RelativeStrength (Baseline Area Chart)

**Files:**
- Create: `frontend/src/components/chart/RelativeStrength.tsx`

- [ ] **Step 1: RelativeStrength 컴포넌트 작성**

```tsx
// frontend/src/components/chart/RelativeStrength.tsx
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
```

- [ ] **Step 2: tsc 확인**

```bash
cd frontend && npx tsc --noEmit
```

- [ ] **Step 3: 커밋**

```bash
git add frontend/src/components/chart/RelativeStrength.tsx
git commit -m "feat: add RelativeStrength baseline area chart vs S&P500"
```

---

## Task 4: RangeChart (52주 Range Bullet)

**Files:**
- Create: `frontend/src/components/chart/RangeChart.tsx`

- [ ] **Step 1: RangeChart 컴포넌트 작성**

```tsx
// frontend/src/components/chart/RangeChart.tsx
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/utils";
import { formatPrice } from "@/lib/utils";
import type { Sector } from "@/types";

interface RangeChartProps {
  sectors: Sector[];
  loading: boolean;
}

function BulletBar({ sector }: { sector: Sector }) {
  // Mock 52-week range — real data will come from EODHD API expansion
  const low52 = sector.price * 0.75;
  const high52 = sector.price * 1.25;
  const range = high52 - low52;
  const position = range > 0 ? ((sector.price - low52) / range) * 100 : 50;

  return (
    <div className="flex items-center gap-3 py-1">
      <span className="w-10 shrink-0 font-mono text-xs text-muted-foreground">
        {sector.etf_symbol}
      </span>
      <span className="w-14 shrink-0 text-right font-mono text-xs text-muted-foreground">
        {formatPrice(low52)}
      </span>
      <div className="relative h-3 flex-1 rounded-full bg-muted/50">
        <div
          className={cn(
            "absolute top-0 h-3 rounded-full",
            sector.change_percent >= 0 ? "bg-bullish/30" : "bg-bearish/30",
          )}
          style={{ width: `${Math.min(position, 100)}%` }}
        />
        <div
          className="absolute top-[-2px] h-[18px] w-[3px] rounded-full bg-foreground"
          style={{ left: `${Math.min(Math.max(position, 0), 100)}%` }}
        />
      </div>
      <span className="w-14 shrink-0 font-mono text-xs text-muted-foreground">
        {formatPrice(high52)}
      </span>
      <span className="w-16 shrink-0 text-right font-mono text-xs font-medium text-foreground">
        {formatPrice(sector.price)}
      </span>
    </div>
  );
}

export function RangeChart({ sectors, loading }: RangeChartProps) {
  if (loading) {
    return (
      <Card>
        <CardHeader><CardTitle>52-Week Range</CardTitle></CardHeader>
        <CardContent className="space-y-2">
          {Array.from({ length: 6 }).map((_, i) => (
            <Skeleton key={i} className="h-5 w-full" />
          ))}
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader><CardTitle>52-Week Range</CardTitle></CardHeader>
      <CardContent>
        {sectors.map((sector) => (
          <BulletBar key={sector.etf_symbol} sector={sector} />
        ))}
      </CardContent>
    </Card>
  );
}
```

- [ ] **Step 2: tsc 확인**

```bash
cd frontend && npx tsc --noEmit
```

- [ ] **Step 3: 커밋**

```bash
git add frontend/src/components/chart/RangeChart.tsx
git commit -m "feat: add RangeChart 52-week bullet chart"
```

---

## Task 5: EventMarker (AI 이벤트 마커)

**Files:**
- Create: `frontend/src/components/chart/EventMarker.tsx`

- [ ] **Step 1: EventMarker 컴포넌트 작성**

```tsx
// frontend/src/components/chart/EventMarker.tsx
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
```

- [ ] **Step 2: tsc 확인**

```bash
cd frontend && npx tsc --noEmit
```

- [ ] **Step 3: 커밋**

```bash
git add frontend/src/components/chart/EventMarker.tsx
git commit -m "feat: add EventMarker for AI rotation signal display"
```

---

## Task 6: MultiChartGrid (2분할 컨테이너)

**Files:**
- Create: `frontend/src/components/chart/MultiChartGrid.tsx`

- [ ] **Step 1: MultiChartGrid 컴포넌트 작성**

```tsx
// frontend/src/components/chart/MultiChartGrid.tsx
import { MomentumBar } from "./MomentumBar";
import { RelativeStrength } from "./RelativeStrength";
import { RangeChart } from "./RangeChart";
import { EventMarker } from "./EventMarker";
import type { RotationSignal, Sector } from "@/types";

interface MultiChartGridProps {
  sectors: Sector[];
  signals: RotationSignal[];
  loading: boolean;
}

export function MultiChartGrid({ sectors, signals, loading }: MultiChartGridProps) {
  return (
    <div className="space-y-4">
      {/* Event Markers */}
      <EventMarker signals={signals} />

      {/* 2-column chart grid */}
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <MomentumBar sectors={sectors} loading={loading} />
        <RelativeStrength sectors={sectors} loading={loading} />
      </div>

      {/* Full-width range chart */}
      <RangeChart sectors={sectors} loading={loading} />
    </div>
  );
}
```

- [ ] **Step 2: tsc 확인**

```bash
cd frontend && npx tsc --noEmit
```

- [ ] **Step 3: 커밋**

```bash
git add frontend/src/components/chart/MultiChartGrid.tsx
git commit -m "feat: add MultiChartGrid 2-column chart container"
```

---

## Task 7: AiScreenerTable

**Files:**
- Create: `frontend/src/components/screener/AiScreenerTable.tsx`

- [ ] **Step 1: 디렉토리 생성**

```bash
mkdir -p frontend/src/components/screener
```

- [ ] **Step 2: AiScreenerTable 컴포넌트 작성**

```tsx
// frontend/src/components/screener/AiScreenerTable.tsx
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/utils";
import { getChangeColor } from "@/lib/utils";
import type { SectorScoreboard } from "@/types";

interface AiScreenerTableProps {
  scoreboards: SectorScoreboard[];
  loading: boolean;
}

function getRecommendationVariant(rec: string): "bullish" | "bearish" | "default" {
  if (rec === "overweight") return "bullish";
  if (rec === "underweight") return "bearish";
  return "default";
}

export function AiScreenerTable({ scoreboards, loading }: AiScreenerTableProps) {
  if (loading) {
    return (
      <Card>
        <CardHeader><CardTitle>AI Sector Screener</CardTitle></CardHeader>
        <CardContent className="space-y-2">
          {Array.from({ length: 5 }).map((_, i) => (
            <Skeleton key={i} className="h-8 w-full" />
          ))}
        </CardContent>
      </Card>
    );
  }

  const sorted = [...scoreboards].sort((a, b) => a.rank - b.rank);

  return (
    <Card>
      <CardHeader><CardTitle>AI Sector Screener</CardTitle></CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border text-xs text-muted-foreground">
                <th className="px-2 py-2 text-left">Rank</th>
                <th className="px-2 py-2 text-left">Sector</th>
                <th className="px-2 py-2 text-left">ETF</th>
                <th className="px-2 py-2 text-right">AI Score</th>
                <th className="px-2 py-2 text-right">Base</th>
                <th className="px-2 py-2 text-right">News</th>
                <th className="px-2 py-2 text-right">Momentum</th>
                <th className="px-2 py-2 text-center">Signal</th>
              </tr>
            </thead>
            <tbody>
              {sorted.map((sb) => (
                <tr
                  key={sb.etf_symbol}
                  className="border-b border-border/50 transition-colors hover:bg-muted/20"
                >
                  <td className="px-2 py-2 font-mono text-xs text-muted-foreground">
                    #{sb.rank}
                  </td>
                  <td className="px-2 py-2 font-medium text-foreground">
                    {sb.sector_name}
                  </td>
                  <td className="px-2 py-2 font-mono text-xs text-muted-foreground">
                    {sb.etf_symbol}
                  </td>
                  <td className={cn("px-2 py-2 text-right font-mono font-bold", getChangeColor(sb.final_score))}>
                    {sb.final_score.toFixed(2)}
                  </td>
                  <td className="px-2 py-2 text-right font-mono text-xs text-muted-foreground">
                    {sb.base_score.toFixed(2)}
                  </td>
                  <td className={cn("px-2 py-2 text-right font-mono text-xs", getChangeColor(sb.news_sentiment_score))}>
                    {sb.news_sentiment_score.toFixed(2)}
                  </td>
                  <td className={cn("px-2 py-2 text-right font-mono text-xs", getChangeColor(sb.momentum_score))}>
                    {sb.momentum_score.toFixed(2)}
                  </td>
                  <td className="px-2 py-2 text-center">
                    <Badge variant={getRecommendationVariant(sb.recommendation)}>
                      {sb.recommendation}
                    </Badge>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {sorted.length === 0 && (
          <p className="py-8 text-center text-sm text-muted-foreground">
            스크리너 데이터 없음
          </p>
        )}
      </CardContent>
    </Card>
  );
}
```

- [ ] **Step 2: tsc 확인**

```bash
cd frontend && npx tsc --noEmit
```

- [ ] **Step 3: 커밋**

```bash
git add frontend/src/components/screener/AiScreenerTable.tsx
git commit -m "feat: add AiScreenerTable with ranked sector scores"
```

---

## Task 8: App.tsx — Area D 통합 (프론트엔드 완성)

**Files:**
- Modify: `frontend/src/App.tsx`

- [ ] **Step 1: App.tsx 교체 — Area D placeholder를 실제 컴포넌트로**

기존 App.tsx를 읽은 후, Area D 섹션과 import를 교체:

import 추가:
```tsx
import { useAnalysisData } from "@/hooks/useAnalysisData";
import { MultiChartGrid } from "@/components/chart/MultiChartGrid";
import { AiScreenerTable } from "@/components/screener/AiScreenerTable";
```

App 함수 내 추가:
```tsx
const analysisData = useAnalysisData();
```

Area D placeholder를 다음으로 교체:
```tsx
      {/* Area D: Deep Dive & Screener */}
      <section className="space-y-4 px-4 pb-4">
        <MultiChartGrid
          sectors={marketData.sectors}
          signals={analysisData.signals}
          loading={marketData.loading}
        />
        <AiScreenerTable
          scoreboards={analysisData.scoreboards}
          loading={analysisData.loading}
        />
      </section>
```

- [ ] **Step 2: tsc 확인**

```bash
cd frontend && npx tsc --noEmit
```

- [ ] **Step 3: 빌드 확인**

```bash
cd frontend && npm run build
```

- [ ] **Step 4: 커밋**

```bash
git add frontend/src/App.tsx
git commit -m "feat: integrate Area D (Charts + AI Screener) — frontend complete"
```
