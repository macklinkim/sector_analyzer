# Phase 4a: Frontend Scaffolding + Area A (Global Macro Header)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Vite + React SPA 프로젝트 스캐폴딩, TypeScript 타입 정의, FastAPI 클라이언트, 4-Area 대시보드 레이아웃 셸, Area A(Global Macro Header) 컴포넌트 구현. 이후 Phase 4b(Area B+C), 4c(Area D)의 기반.

**Architecture:** Vite + React 19 SPA (CSR). shadcn/ui + Tailwind CSS dark mode. FastAPI 백엔드(`http://localhost:8000`)에서 데이터 fetch. 4-Area CSS Grid 레이아웃. 컴포넌트별 커스텀 훅으로 데이터 로딩 분리.

**Tech Stack:** Vite, React 19, TypeScript (strict), Tailwind CSS, shadcn/ui, Recharts, Lucide Icons

**Spec:** `docs/superpowers/specs/2026-04-05-market-insights-dashboard-design.md` (Section 5, 6)
**Frontend Rules:** `.claude/rules/frontend.md`

**Scope:** Phase 4는 프론트엔드 전체를 3개 서브 플랜으로 분할:
- **4a (이 플랜)**: 스캐폴딩 + 타입 + API + 레이아웃 + Area A
- **4b**: Area B (Sector Heatmap & Movers) + Area C (News & Calendar)
- **4c**: Area D (Charts & AI Screener)

---

## File Map

| Action | Path | Responsibility |
|--------|------|----------------|
| Create | `frontend/package.json` | 프로젝트 메타 + 의존성 (Vite scaffold) |
| Create | `frontend/vite.config.ts` | Vite 설정 + proxy |
| Create | `frontend/tsconfig.json` | TypeScript strict 설정 |
| Create | `frontend/tsconfig.app.json` | 앱용 TS 설정 |
| Create | `frontend/tsconfig.node.json` | 노드용 TS 설정 |
| — | ~~`tailwind.config.ts`~~ | Tailwind v4 + @tailwindcss/vite 사용 → 불필요 |
| — | ~~`postcss.config.js`~~ | Tailwind v4 Vite 플러그인이 대체 → 불필요 |
| Create | `frontend/index.html` | SPA 진입 HTML |
| Create | `frontend/src/main.tsx` | React 진입점 |
| Create | `frontend/src/index.css` | Tailwind 디렉티브 + CSS 변수 |
| Create | `frontend/src/lib/utils.ts` | cn() 유틸리티 (shadcn/ui 필수) |
| Create | `frontend/src/types/index.ts` | 공유 TypeScript 타입 |
| Create | `frontend/src/lib/api.ts` | FastAPI fetch wrapper |
| Create | `frontend/src/hooks/useMarketData.ts` | Market 데이터 커스텀 훅 |
| Create | `frontend/src/App.tsx` | 4-Area 그리드 레이아웃 |
| Create | `frontend/src/components/ui/skeleton.tsx` | Skeleton 로딩 (shadcn/ui) |
| Create | `frontend/src/components/ui/badge.tsx` | Badge 컴포넌트 (shadcn/ui) |
| Create | `frontend/src/components/ui/card.tsx` | Card 컴포넌트 (shadcn/ui) |
| Create | `frontend/src/components/header/GlobalMacroHeader.tsx` | Area A 컨테이너 |
| Create | `frontend/src/components/header/TickerBar.tsx` | 지수 + 거시지표 티커 |
| Create | `frontend/src/components/header/RegimeBadge.tsx` | 매크로 국면 배지 |

---

## Task 1: Vite + React 프로젝트 스캐폴딩

**Files:**
- Create: `frontend/` 디렉토리 전체 (Vite scaffold)

- [ ] **Step 1: Vite로 React + TypeScript 프로젝트 생성**

```bash
cd C:/Users/mack/Desktop/projects/study/economi_analyzer
npm create vite@latest frontend -- --template react-ts
```

Expected: `frontend/` 디렉토리 생성됨

- [ ] **Step 2: 의존성 설치**

```bash
cd frontend && npm install
```

- [ ] **Step 3: 추가 의존성 설치**

```bash
cd frontend && npm install recharts lucide-react class-variance-authority clsx tailwind-merge
```

> - `recharts`: 차트 라이브러리
> - `lucide-react`: 아이콘
> - `class-variance-authority`, `clsx`, `tailwind-merge`: shadcn/ui 필수 유틸

- [ ] **Step 4: Tailwind CSS v4 설치**

```bash
cd frontend && npm install tailwindcss @tailwindcss/vite
```

- [ ] **Step 5: vite.config.ts에 Tailwind 플러그인 + API proxy 설정**

`frontend/vite.config.ts`를 다음으로 교체:

```ts
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";
import path from "path";

export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
      "/health": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },
});
```

- [ ] **Step 6: index.css에 Tailwind 디렉티브 + Dark Mode CSS 변수 설정**

`frontend/src/index.css`를 다음으로 교체:

```css
@import "tailwindcss";

@theme {
  /* Dark mode base colors */
  --color-background: #0f172a;
  --color-foreground: #f8fafc;
  --color-card: #1e293b;
  --color-card-foreground: #f1f5f9;
  --color-border: #334155;
  --color-muted: #334155;
  --color-muted-foreground: #94a3b8;

  /* Market colors */
  --color-bullish: #22c55e;
  --color-bearish: #ef4444;

  /* Regime colors */
  --color-goldilocks: #22c55e;
  --color-reflation: #f59e0b;
  --color-stagflation: #ef4444;
  --color-deflation: #3b82f6;

  /* Impact score colors */
  --color-impact-low: #6b7280;
  --color-impact-medium: #f59e0b;
  --color-impact-high: #ef4444;
}

body {
  background-color: var(--color-background);
  color: var(--color-foreground);
  font-family: "Inter", system-ui, -apple-system, sans-serif;
}
```

- [ ] **Step 7: Vite scaffold가 생성한 불필요 파일 정리**

```bash
cd frontend && rm -f src/App.css src/assets/react.svg public/vite.svg
```

- [ ] **Step 8: 개발 서버 실행 확인**

```bash
cd frontend && npm run dev
```

Expected: `http://localhost:5173`에서 앱 로딩 (빈 화면 OK)

- [ ] **Step 9: 커밋**

```bash
cd C:/Users/mack/Desktop/projects/study/economi_analyzer
git add frontend/
git commit -m "feat: scaffold Vite + React + TypeScript frontend with Tailwind CSS"
```

---

## Task 2: TypeScript 타입 정의

**Files:**
- Create: `frontend/src/types/index.ts`

- [ ] **Step 1: 공유 타입 파일 작성**

```ts
// frontend/src/types/index.ts

// --- Market Types ---

export interface MarketIndex {
  symbol: string;
  name: string;
  price: number;
  change_percent: number;
  collected_at: string;
}

export interface Sector {
  name: string;
  etf_symbol: string;
  price: number;
  change_percent: number;
  volume: number;
  avg_volume_20d: number | null;
  volume_change_percent: number | null;
  relative_strength: number | null;
  momentum_1w: number | null;
  momentum_1m: number | null;
  momentum_3m: number | null;
  momentum_6m: number | null;
  rs_rank: number | null;
  collected_at: string;
}

export interface EconomicIndicator {
  indicator_name: string;
  value: number;
  previous_value: number | null;
  change_direction: string;
  source: string;
  reported_at: string;
}

// --- News Types ---

export interface NewsArticle {
  category: string;
  title: string;
  source: string;
  url: string;
  summary: string | null;
  published_at: string;
  collected_at: string;
}

export interface NewsImpactAnalysis {
  news_url: string;
  sector_name: string;
  impact_score: number;
  impact_direction: string;
  reasoning: string;
  rotation_relevance: number;
  batch_type: string;
  analyzed_at: string;
}

// --- Analysis Types ---

export interface MacroRegime {
  regime: "goldilocks" | "reflation" | "stagflation" | "deflation";
  growth_direction: string;
  inflation_direction: string;
  transition_from: string | null;
  transition_probability: number | null;
  regime_probabilities: Record<string, number>;
  indicators_snapshot: Record<string, unknown> | null;
  reasoning: string;
  batch_type: string;
  analyzed_at: string;
}

export interface SectorScoreboard {
  sector_name: string;
  etf_symbol: string;
  base_score: number;
  override_score: number;
  news_sentiment_score: number;
  momentum_score: number;
  final_score: number;
  rank: number;
  recommendation: "overweight" | "neutral" | "underweight";
  reasoning: string;
  batch_type: string;
  scored_at: string;
}

export interface RotationSignal {
  signal_type: string;
  from_sector: string | null;
  to_sector: string | null;
  strength: number;
  base_score: number | null;
  override_adjustment: number | null;
  final_score: number;
  reasoning: string;
  supporting_news_urls: string[];
  batch_type: string;
  detected_at: string;
}

export interface MarketReport {
  batch_type: string;
  summary: string;
  key_highlights: string[];
  regime: MacroRegime;
  top_sectors: SectorScoreboard[];
  bottom_sectors: SectorScoreboard[];
  rotation_signals: RotationSignal[];
  report_date: string;
  analyzed_at: string;
  disclaimer: string;
}

// --- Regime Helpers ---

export type RegimeType = MacroRegime["regime"];

export const REGIME_COLORS: Record<RegimeType, string> = {
  goldilocks: "var(--color-goldilocks)",
  reflation: "var(--color-reflation)",
  stagflation: "var(--color-stagflation)",
  deflation: "var(--color-deflation)",
};

export const REGIME_LABELS: Record<RegimeType, string> = {
  goldilocks: "Goldilocks",
  reflation: "Reflation",
  stagflation: "Stagflation",
  deflation: "Deflation",
};
```

- [ ] **Step 2: TypeScript 컴파일 확인**

```bash
cd frontend && npx tsc --noEmit
```

Expected: 에러 없음

- [ ] **Step 3: 커밋**

```bash
git add frontend/src/types/index.ts
git commit -m "feat: add TypeScript type definitions for market, news, analysis data"
```

---

## Task 3: 유틸리티 + API 클라이언트

**Files:**
- Create: `frontend/src/lib/utils.ts`
- Create: `frontend/src/lib/api.ts`

- [ ] **Step 1: cn() 유틸리티 작성 (shadcn/ui 필수)**

```ts
// frontend/src/lib/utils.ts
import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatPercent(value: number): string {
  const sign = value >= 0 ? "+" : "";
  return `${sign}${value.toFixed(2)}%`;
}

export function formatPrice(value: number): string {
  return value.toLocaleString("en-US", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
}

export function formatCompactNumber(value: number): string {
  return Intl.NumberFormat("en-US", { notation: "compact" }).format(value);
}

export function getChangeColor(value: number): string {
  if (value > 0) return "text-bullish";
  if (value < 0) return "text-bearish";
  return "text-muted-foreground";
}

export function getImpactColor(score: number): string {
  if (score >= 7) return "bg-impact-high text-white";
  if (score >= 4) return "bg-impact-medium text-black";
  return "bg-impact-low text-white";
}
```

- [ ] **Step 2: API 클라이언트 작성**

```ts
// frontend/src/lib/api.ts
import type {
  EconomicIndicator,
  MacroRegime,
  MarketIndex,
  MarketReport,
  NewsArticle,
  NewsImpactAnalysis,
  RotationSignal,
  Sector,
  SectorScoreboard,
} from "@/types";

const BASE_URL = "/api";

async function fetchJson<T>(path: string): Promise<T> {
  const response = await fetch(`${BASE_URL}${path}`);
  if (!response.ok) {
    throw new Error(`API error: ${response.status} ${response.statusText}`);
  }
  return response.json();
}

// Market
export const api = {
  getIndices: () => fetchJson<MarketIndex[]>("/market/indices"),
  getSectors: () => fetchJson<Sector[]>("/market/sectors"),
  getIndicators: () => fetchJson<EconomicIndicator[]>("/market/indicators"),
  getRegime: () => fetchJson<MacroRegime>("/market/regime"),

  // News
  getNewsArticles: (category?: string, limit = 20) => {
    const params = new URLSearchParams();
    if (category) params.set("category", category);
    params.set("limit", String(limit));
    return fetchJson<NewsArticle[]>(`/news/articles?${params}`);
  },
  getNewsImpacts: () => fetchJson<NewsImpactAnalysis[]>("/news/impacts"),

  // Analysis
  getReport: () => fetchJson<MarketReport>("/analysis/report"),
  getScoreboards: (batchType = "pre_market") =>
    fetchJson<SectorScoreboard[]>(`/analysis/scoreboards?batch_type=${batchType}`),
  getSignals: () => fetchJson<RotationSignal[]>("/analysis/signals"),
};
```

- [ ] **Step 3: TypeScript 컴파일 확인**

```bash
cd frontend && npx tsc --noEmit
```

Expected: 에러 없음

- [ ] **Step 4: 커밋**

```bash
git add frontend/src/lib/utils.ts frontend/src/lib/api.ts
git commit -m "feat: add utility functions and FastAPI client"
```

---

## Task 4: shadcn/ui 기본 컴포넌트

**Files:**
- Create: `frontend/src/components/ui/skeleton.tsx`
- Create: `frontend/src/components/ui/badge.tsx`
- Create: `frontend/src/components/ui/card.tsx`

- [ ] **Step 1: Skeleton 컴포넌트 작성**

```tsx
// frontend/src/components/ui/skeleton.tsx
import { cn } from "@/lib/utils";

function Skeleton({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn("animate-pulse rounded-md bg-muted", className)}
      {...props}
    />
  );
}

export { Skeleton };
```

- [ ] **Step 2: Badge 컴포넌트 작성**

```tsx
// frontend/src/components/ui/badge.tsx
import { type VariantProps, cva } from "class-variance-authority";
import { cn } from "@/lib/utils";

const badgeVariants = cva(
  "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors",
  {
    variants: {
      variant: {
        default: "border-transparent bg-slate-700 text-slate-100",
        bullish: "border-transparent bg-bullish/20 text-bullish",
        bearish: "border-transparent bg-bearish/20 text-bearish",
        goldilocks: "border-transparent bg-goldilocks/20 text-goldilocks",
        reflation: "border-transparent bg-reflation/20 text-reflation",
        stagflation: "border-transparent bg-stagflation/20 text-stagflation",
        deflation: "border-transparent bg-deflation/20 text-deflation",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  },
);

interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
  return <div className={cn(badgeVariants({ variant }), className)} {...props} />;
}

export { Badge, badgeVariants };
```

- [ ] **Step 3: Card 컴포넌트 작성**

```tsx
// frontend/src/components/ui/card.tsx
import { cn } from "@/lib/utils";

function Card({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn("rounded-xl border border-border bg-card text-card-foreground", className)}
      {...props}
    />
  );
}

function CardHeader({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return <div className={cn("flex flex-col space-y-1.5 p-4", className)} {...props} />;
}

function CardTitle({ className, ...props }: React.HTMLAttributes<HTMLHeadingElement>) {
  return <h3 className={cn("text-sm font-semibold leading-none tracking-tight", className)} {...props} />;
}

function CardContent({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return <div className={cn("p-4 pt-0", className)} {...props} />;
}

export { Card, CardHeader, CardTitle, CardContent };
```

- [ ] **Step 4: TypeScript 컴파일 확인**

```bash
cd frontend && npx tsc --noEmit
```

- [ ] **Step 5: 커밋**

```bash
git add frontend/src/components/ui/
git commit -m "feat: add shadcn/ui base components (Skeleton, Badge, Card)"
```

---

## Task 5: 커스텀 훅 — useMarketData

**Files:**
- Create: `frontend/src/hooks/useMarketData.ts`

- [ ] **Step 1: useMarketData 훅 작성**

```ts
// frontend/src/hooks/useMarketData.ts
import { useCallback, useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { EconomicIndicator, MacroRegime, MarketIndex, Sector } from "@/types";

interface MarketData {
  indices: MarketIndex[];
  sectors: Sector[];
  indicators: EconomicIndicator[];
  regime: MacroRegime | null;
  loading: boolean;
  error: string | null;
  lastUpdated: string | null;
}

export function useMarketData(): MarketData & { refresh: () => void } {
  const [data, setData] = useState<MarketData>({
    indices: [],
    sectors: [],
    indicators: [],
    regime: null,
    loading: true,
    error: null,
    lastUpdated: null,
  });

  const fetchData = useCallback(async () => {
    setData((prev) => ({ ...prev, loading: true, error: null }));
    try {
      const [indices, sectors, indicators, regime] = await Promise.all([
        api.getIndices(),
        api.getSectors(),
        api.getIndicators(),
        api.getRegime().catch(() => null),
      ]);
      setData({
        indices,
        sectors,
        indicators,
        regime,
        loading: false,
        error: null,
        lastUpdated: new Date().toISOString(),
      });
    } catch (err) {
      setData((prev) => ({
        ...prev,
        loading: false,
        error: err instanceof Error ? err.message : "Failed to fetch data",
      }));
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return { ...data, refresh: fetchData };
}
```

- [ ] **Step 2: TypeScript 컴파일 확인**

```bash
cd frontend && npx tsc --noEmit
```

- [ ] **Step 3: 커밋**

```bash
git add frontend/src/hooks/useMarketData.ts
git commit -m "feat: add useMarketData custom hook for parallel data fetching"
```

---

## Task 6: 4-Area 레이아웃 셸 (App.tsx)

**Files:**
- Modify: `frontend/src/App.tsx`

- [ ] **Step 1: App.tsx 작성 (4-Area 그리드 + placeholder)**

```tsx
// frontend/src/App.tsx
import { useMarketData } from "@/hooks/useMarketData";
import { GlobalMacroHeader } from "@/components/header/GlobalMacroHeader";

export default function App() {
  const marketData = useMarketData();

  return (
    <div className="min-h-screen bg-background text-foreground">
      {/* Area A: Global Macro Header */}
      <header>
        <GlobalMacroHeader
          indices={marketData.indices}
          indicators={marketData.indicators}
          regime={marketData.regime}
          loading={marketData.loading}
          lastUpdated={marketData.lastUpdated}
        />
      </header>

      {/* Area B + C: Side by side */}
      <main className="grid grid-cols-1 gap-4 p-4 lg:grid-cols-2">
        {/* Area B: Sector Heatmap & Movers */}
        <section className="rounded-xl border border-border bg-card p-4">
          <h2 className="mb-2 text-sm font-semibold text-muted-foreground">
            Sector Heatmap & Market Movers
          </h2>
          <p className="text-xs text-muted-foreground">Phase 4b에서 구현</p>
        </section>

        {/* Area C: News Impact & Calendar */}
        <section className="rounded-xl border border-border bg-card p-4">
          <h2 className="mb-2 text-sm font-semibold text-muted-foreground">
            News Impact & Calendar
          </h2>
          <p className="text-xs text-muted-foreground">Phase 4b에서 구현</p>
        </section>
      </main>

      {/* Area D: Deep Dive & Screener */}
      <section className="mx-4 mb-4 rounded-xl border border-border bg-card p-4">
        <h2 className="mb-2 text-sm font-semibold text-muted-foreground">
          Interactive Deep Dive & AI Screener
        </h2>
        <p className="text-xs text-muted-foreground">Phase 4c에서 구현</p>
      </section>

      {/* Disclaimer */}
      <footer className="border-t border-border px-4 py-3 text-center text-xs text-muted-foreground">
        본 분석은 AI의 추론이며, 실제 투자 판단의 근거로 사용할 수 없습니다.
      </footer>
    </div>
  );
}
```

- [ ] **Step 2: main.tsx 정리**

`frontend/src/main.tsx`를 다음으로 교체:

```tsx
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import App from "./App";
import "./index.css";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
```

- [ ] **Step 3: 개발 서버 실행 + 확인**

```bash
cd frontend && npm run dev
```

Expected: Dark mode 배경, 4-Area placeholder 레이아웃 렌더링

- [ ] **Step 4: 커밋**

```bash
git add frontend/src/App.tsx frontend/src/main.tsx
git commit -m "feat: add 4-Area dashboard layout shell with placeholders"
```

---

## Task 7: Area A — GlobalMacroHeader + TickerBar + RegimeBadge

**Files:**
- Create: `frontend/src/components/header/GlobalMacroHeader.tsx`
- Create: `frontend/src/components/header/TickerBar.tsx`
- Create: `frontend/src/components/header/RegimeBadge.tsx`

- [ ] **Step 1: RegimeBadge 컴포넌트 작성**

```tsx
// frontend/src/components/header/RegimeBadge.tsx
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import type { MacroRegime, RegimeType } from "@/types";
import { REGIME_LABELS } from "@/types";

interface RegimeBadgeProps {
  regime: MacroRegime | null;
  loading: boolean;
}

export function RegimeBadge({ regime, loading }: RegimeBadgeProps) {
  if (loading) {
    return <Skeleton className="h-6 w-40" />;
  }

  if (!regime) {
    return (
      <Badge variant="default">
        국면 데이터 없음
      </Badge>
    );
  }

  const regimeType = regime.regime as RegimeType;
  const confidence = regime.regime_probabilities[regimeType];
  const confidencePercent = confidence ? `${(confidence * 100).toFixed(0)}%` : "";

  return (
    <div className="flex items-center gap-2">
      <span className="text-xs text-muted-foreground">현재 국면:</span>
      <Badge variant={regimeType}>
        {REGIME_LABELS[regimeType]} {confidencePercent && `(${confidencePercent})`}
      </Badge>
    </div>
  );
}
```

- [ ] **Step 2: TickerBar 컴포넌트 작성**

```tsx
// frontend/src/components/header/TickerBar.tsx
import { Skeleton } from "@/components/ui/skeleton";
import { formatPercent, formatPrice, getChangeColor } from "@/lib/utils";
import type { EconomicIndicator, MarketIndex } from "@/types";

interface TickerBarProps {
  indices: MarketIndex[];
  indicators: EconomicIndicator[];
  loading: boolean;
}

const INDICATOR_DISPLAY: Record<string, { label: string; prefix?: string }> = {
  US10Y: { label: "US10Y" },
  DXY: { label: "DXY" },
  WTI: { label: "WTI", prefix: "$" },
  GOLD: { label: "Gold", prefix: "$" },
};

export function TickerBar({ indices, indicators, loading }: TickerBarProps) {
  if (loading) {
    return (
      <div className="flex gap-6">
        {Array.from({ length: 7 }).map((_, i) => (
          <Skeleton key={i} className="h-5 w-28" />
        ))}
      </div>
    );
  }

  return (
    <div className="flex flex-wrap items-center gap-x-6 gap-y-1">
      {/* Indices */}
      {indices.map((idx) => (
        <div key={idx.symbol} className="flex items-center gap-1.5 text-sm">
          <span className="font-medium text-foreground">{idx.name}</span>
          <span className={getChangeColor(idx.change_percent)}>
            {formatPercent(idx.change_percent)}
          </span>
        </div>
      ))}

      {/* Divider */}
      {indices.length > 0 && indicators.length > 0 && (
        <div className="h-4 w-px bg-border" />
      )}

      {/* Economic Indicators */}
      {indicators.map((ind) => {
        const display = INDICATOR_DISPLAY[ind.indicator_name];
        if (!display) return null;
        return (
          <div key={ind.indicator_name} className="flex items-center gap-1.5 text-sm">
            <span className="text-muted-foreground">{display.label}</span>
            <span className="font-medium text-foreground">
              {display.prefix ?? ""}{formatPrice(ind.value)}
            </span>
          </div>
        );
      })}
    </div>
  );
}
```

- [ ] **Step 3: GlobalMacroHeader 컨테이너 작성**

```tsx
// frontend/src/components/header/GlobalMacroHeader.tsx
import { RegimeBadge } from "./RegimeBadge";
import { TickerBar } from "./TickerBar";
import type { EconomicIndicator, MacroRegime, MarketIndex } from "@/types";

interface GlobalMacroHeaderProps {
  indices: MarketIndex[];
  indicators: EconomicIndicator[];
  regime: MacroRegime | null;
  loading: boolean;
  lastUpdated: string | null;
}

export function GlobalMacroHeader({
  indices,
  indicators,
  regime,
  loading,
  lastUpdated,
}: GlobalMacroHeaderProps) {
  return (
    <div className="border-b border-border bg-card px-4 py-3">
      <div className="flex flex-col gap-2 lg:flex-row lg:items-center lg:justify-between">
        {/* Row 1: Ticker Bar */}
        <TickerBar indices={indices} indicators={indicators} loading={loading} />

        {/* Row 2: Regime + Status */}
        <div className="flex items-center gap-4">
          <RegimeBadge regime={regime} loading={loading} />
          {loading && (
            <span className="text-xs text-muted-foreground animate-pulse">
              AI 분석중...
            </span>
          )}
          {lastUpdated && !loading && (
            <span className="text-xs text-muted-foreground">
              갱신: {new Date(lastUpdated).toLocaleTimeString("ko-KR", { hour: "2-digit", minute: "2-digit" })}
            </span>
          )}
        </div>
      </div>
    </div>
  );
}
```

- [ ] **Step 4: TypeScript 컴파일 확인**

```bash
cd frontend && npx tsc --noEmit
```

Expected: 에러 없음

- [ ] **Step 5: 개발 서버에서 시각적 확인**

```bash
cd frontend && npm run dev
```

Expected: 상단에 헤더 바 렌더링 (API 연결 없으면 Skeleton 로딩 → 에러 후 빈 상태)

- [ ] **Step 6: 빌드 확인**

```bash
cd frontend && npm run build
```

Expected: `dist/` 생성, 에러 없음

- [ ] **Step 7: 커밋**

```bash
git add frontend/src/components/header/
git commit -m "feat: add Area A — GlobalMacroHeader, TickerBar, RegimeBadge"
```

---

## Task 8: 최종 검증

- [ ] **Step 1: TypeScript 전체 컴파일 확인**

```bash
cd frontend && npx tsc --noEmit
```

Expected: 에러 없음

- [ ] **Step 2: 빌드**

```bash
cd frontend && npm run build
```

Expected: 성공

- [ ] **Step 3: 최종 커밋 (필요 시)**

```bash
git add -A && git commit -m "chore: Phase 4a frontend scaffold + Area A complete"
```
