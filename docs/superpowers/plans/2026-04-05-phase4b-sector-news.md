# Phase 4b: Area B (Sector Heatmap & Movers) + Area C (News & Calendar)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 대시보드 Area B(섹터 히트맵 + Market Movers)와 Area C(뉴스 임팩트 피드 + 경제 캘린더) 컴포넌트 구현. Phase 4a의 placeholder를 실제 컴포넌트로 교체.

**Architecture:** Area B는 Recharts Treemap으로 11개 섹터 히트맵 + 섹터 클릭 시 Market Movers 리스트 전환. Area C는 탭 기반 뉴스 피드(4카테고리) + Impact Score 뱃지 + 경제 캘린더. 각 Area별 커스텀 훅으로 데이터 로딩 분리.

**Tech Stack:** React 19, Recharts (Treemap, Sparkline), Tailwind CSS v4, shadcn/ui (Card, Badge, Skeleton)

**Spec:** `docs/superpowers/specs/2026-04-05-market-insights-dashboard-design.md` (Section 5.2, 5.3)
**Frontend Rules:** `.claude/rules/frontend.md`
**Existing code:** `frontend/src/` — types, api, utils, hooks, ui components 이미 존재 (Phase 4a)

---

## File Map

| Action | Path | Responsibility |
|--------|------|----------------|
| Create | `frontend/src/hooks/useNewsData.ts` | 뉴스 + 임팩트 데이터 fetch 훅 |
| Create | `frontend/src/components/sector/SectorHeatmap.tsx` | Recharts Treemap 히트맵 |
| Create | `frontend/src/components/sector/SectorSparkline.tsx` | 섹터 리스트 + 30일 미니 차트 |
| Create | `frontend/src/components/sector/MarketMovers.tsx` | 섹터 내 급등/급락/거래량 Top5 |
| Create | `frontend/src/components/news/NewsImpactFeed.tsx` | 탭 뉴스 피드 컨테이너 |
| Create | `frontend/src/components/news/ImpactCard.tsx` | 뉴스 카드 + Impact Score 뱃지 |
| Create | `frontend/src/components/news/EconomicCalendar.tsx` | 경제 캘린더 위젯 |
| Modify | `frontend/src/App.tsx` | placeholder → 실제 컴포넌트 교체 |

---

## Task 1: useNewsData 커스텀 훅

**Files:**
- Create: `frontend/src/hooks/useNewsData.ts`

- [ ] **Step 1: useNewsData 훅 작성**

```ts
// frontend/src/hooks/useNewsData.ts
import { useCallback, useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { NewsArticle, NewsImpactAnalysis } from "@/types";

interface NewsData {
  articles: NewsArticle[];
  impacts: NewsImpactAnalysis[];
  loading: boolean;
  error: string | null;
}

export function useNewsData(category?: string): NewsData & { refresh: () => void } {
  const [data, setData] = useState<NewsData>({
    articles: [],
    impacts: [],
    loading: true,
    error: null,
  });

  const fetchData = useCallback(async () => {
    setData((prev) => ({ ...prev, loading: true, error: null }));
    try {
      const [articles, impacts] = await Promise.all([
        api.getNewsArticles(category),
        api.getNewsImpacts(),
      ]);
      setData({ articles, impacts, loading: false, error: null });
    } catch (err) {
      setData((prev) => ({
        ...prev,
        loading: false,
        error: err instanceof Error ? err.message : "Failed to fetch news",
      }));
    }
  }, [category]);

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
git add frontend/src/hooks/useNewsData.ts
git commit -m "feat: add useNewsData custom hook for news + impacts fetching"
```

---

## Task 2: SectorHeatmap (Recharts Treemap)

**Files:**
- Create: `frontend/src/components/sector/SectorHeatmap.tsx`

- [ ] **Step 1: 디렉토리 생성**

```bash
mkdir -p frontend/src/components/sector
```

- [ ] **Step 2: SectorHeatmap 컴포넌트 작성**

```tsx
// frontend/src/components/sector/SectorHeatmap.tsx
import { Treemap, ResponsiveContainer } from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { formatPercent } from "@/lib/utils";
import type { Sector } from "@/types";

interface SectorHeatmapProps {
  sectors: Sector[];
  loading: boolean;
  onSectorClick?: (sectorName: string) => void;
}

function getHeatmapColor(changePercent: number): string {
  if (changePercent >= 2) return "#15803d";
  if (changePercent >= 1) return "#16a34a";
  if (changePercent > 0) return "#22c55e";
  if (changePercent === 0) return "#6b7280";
  if (changePercent > -1) return "#ef4444";
  if (changePercent > -2) return "#dc2626";
  return "#b91c1c";
}

interface TreemapContentProps {
  x: number;
  y: number;
  width: number;
  height: number;
  name: string;
  change_percent: number;
}

function CustomTreemapContent({ x, y, width, height, name, change_percent }: TreemapContentProps) {
  if (width < 40 || height < 30) return null;

  return (
    <g>
      <rect
        x={x}
        y={y}
        width={width}
        height={height}
        rx={4}
        fill={getHeatmapColor(change_percent)}
        stroke="var(--color-background)"
        strokeWidth={2}
      />
      {width > 60 && (
        <>
          <text
            x={x + width / 2}
            y={y + height / 2 - 6}
            textAnchor="middle"
            fill="white"
            fontSize={width > 100 ? 12 : 10}
            fontWeight="bold"
          >
            {name}
          </text>
          <text
            x={x + width / 2}
            y={y + height / 2 + 10}
            textAnchor="middle"
            fill="white"
            fontSize={10}
          >
            {formatPercent(change_percent)}
          </text>
        </>
      )}
    </g>
  );
}

export function SectorHeatmap({ sectors, loading, onSectorClick }: SectorHeatmapProps) {
  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Sector Heatmap</CardTitle>
        </CardHeader>
        <CardContent>
          <Skeleton className="h-64 w-full" />
        </CardContent>
      </Card>
    );
  }

  const treemapData = sectors.map((s) => ({
    name: s.name,
    size: s.volume || 1,
    change_percent: s.change_percent,
    etf_symbol: s.etf_symbol,
  }));

  return (
    <Card>
      <CardHeader>
        <CardTitle>Sector Heatmap</CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={280}>
          <Treemap
            data={treemapData}
            dataKey="size"
            stroke="none"
            content={<CustomTreemapContent x={0} y={0} width={0} height={0} name="" change_percent={0} />}
            onClick={(node) => {
              if (onSectorClick && node?.name) {
                onSectorClick(node.name as string);
              }
            }}
          />
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
git add frontend/src/components/sector/SectorHeatmap.tsx
git commit -m "feat: add SectorHeatmap with Recharts Treemap"
```

---

## Task 3: SectorSparkline (리스트 + 미니 차트)

**Files:**
- Create: `frontend/src/components/sector/SectorSparkline.tsx`

- [ ] **Step 1: SectorSparkline 컴포넌트 작성**

```tsx
// frontend/src/components/sector/SectorSparkline.tsx
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
  // Generate mock sparkline data (30 days) — real data will come from API later
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
```

- [ ] **Step 2: tsc 확인**

```bash
cd frontend && npx tsc --noEmit
```

- [ ] **Step 3: 커밋**

```bash
git add frontend/src/components/sector/SectorSparkline.tsx
git commit -m "feat: add SectorSparkline list with mini charts"
```

---

## Task 4: MarketMovers (급등/급락/거래량 Top5)

**Files:**
- Create: `frontend/src/components/sector/MarketMovers.tsx`

- [ ] **Step 1: MarketMovers 컴포넌트 작성**

```tsx
// frontend/src/components/sector/MarketMovers.tsx
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import { formatCompactNumber, formatPercent, getChangeColor } from "@/lib/utils";
import type { Sector } from "@/types";

interface MarketMoversProps {
  sectors: Sector[];
  selectedSector: string | null;
}

interface MoverItem {
  symbol: string;
  name: string;
  value: string;
  colorClass: string;
}

function MoverList({ title, items }: { title: string; items: MoverItem[] }) {
  if (items.length === 0) return null;

  return (
    <div>
      <h4 className="mb-2 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
        {title}
      </h4>
      <div className="space-y-1">
        {items.map((item) => (
          <div
            key={item.symbol}
            className="flex items-center justify-between rounded px-2 py-1 text-sm"
          >
            <div className="flex items-center gap-2">
              <span className="font-mono text-xs text-muted-foreground">{item.symbol}</span>
              <span className="text-foreground">{item.name}</span>
            </div>
            <span className={cn("font-mono text-xs", item.colorClass)}>{item.value}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

export function MarketMovers({ sectors, selectedSector }: MarketMoversProps) {
  if (!selectedSector) {
    return (
      <Card>
        <CardContent className="py-8 text-center text-sm text-muted-foreground">
          섹터를 클릭하면 Market Movers를 표시합니다
        </CardContent>
      </Card>
    );
  }

  // Sort sectors for top gainers / losers / volume
  const sorted = [...sectors];
  const topGainers: MoverItem[] = sorted
    .sort((a, b) => b.change_percent - a.change_percent)
    .slice(0, 5)
    .map((s) => ({
      symbol: s.etf_symbol,
      name: s.name,
      value: formatPercent(s.change_percent),
      colorClass: getChangeColor(s.change_percent),
    }));

  const topLosers: MoverItem[] = [...sectors]
    .sort((a, b) => a.change_percent - b.change_percent)
    .slice(0, 5)
    .map((s) => ({
      symbol: s.etf_symbol,
      name: s.name,
      value: formatPercent(s.change_percent),
      colorClass: getChangeColor(s.change_percent),
    }));

  const topVolume: MoverItem[] = [...sectors]
    .sort((a, b) => b.volume - a.volume)
    .slice(0, 5)
    .map((s) => ({
      symbol: s.etf_symbol,
      name: s.name,
      value: formatCompactNumber(s.volume),
      colorClass: "text-foreground",
    }));

  return (
    <Card>
      <CardHeader>
        <CardTitle>Market Movers — {selectedSector}</CardTitle>
      </CardHeader>
      <CardContent className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <MoverList title="🔼 Top Gainers" items={topGainers} />
        <MoverList title="🔽 Top Losers" items={topLosers} />
        <MoverList title="📊 Top Volume" items={topVolume} />
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
git add frontend/src/components/sector/MarketMovers.tsx
git commit -m "feat: add MarketMovers with gainers, losers, volume lists"
```

---

## Task 5: ImpactCard (뉴스 카드 + Impact Score 뱃지)

**Files:**
- Create: `frontend/src/components/news/ImpactCard.tsx`

- [ ] **Step 1: 디렉토리 생성**

```bash
mkdir -p frontend/src/components/news
```

- [ ] **Step 2: ImpactCard 컴포넌트 작성**

```tsx
// frontend/src/components/news/ImpactCard.tsx
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import { getImpactColor } from "@/lib/utils";
import type { NewsArticle, NewsImpactAnalysis } from "@/types";

interface ImpactCardProps {
  article: NewsArticle;
  impact?: NewsImpactAnalysis;
}

function timeAgo(dateStr: string): string {
  const diff = Date.now() - new Date(dateStr).getTime();
  const hours = Math.floor(diff / 3600000);
  if (hours < 1) return "방금 전";
  if (hours < 24) return `${hours}시간 전`;
  const days = Math.floor(hours / 24);
  return `${days}일 전`;
}

export function ImpactCard({ article, impact }: ImpactCardProps) {
  return (
    <a
      href={article.url}
      target="_blank"
      rel="noopener noreferrer"
      className="block rounded-lg border border-border p-3 transition-colors hover:bg-muted/30"
    >
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0 flex-1">
          <h4 className="line-clamp-2 text-sm font-medium text-foreground">
            {article.title}
          </h4>
          <div className="mt-1 flex items-center gap-2 text-xs text-muted-foreground">
            <span>{article.source}</span>
            <span>·</span>
            <span>{timeAgo(article.published_at)}</span>
          </div>
          {article.summary && (
            <p className="mt-1 line-clamp-2 text-xs text-muted-foreground">
              {article.summary}
            </p>
          )}
        </div>

        {impact && (
          <div className="flex shrink-0 flex-col items-end gap-1">
            <span
              className={cn(
                "inline-flex h-6 w-6 items-center justify-center rounded-full text-xs font-bold",
                getImpactColor(impact.impact_score),
              )}
            >
              {impact.impact_score}
            </span>
            <Badge
              variant={impact.impact_direction === "positive" ? "bullish" : "bearish"}
              className="text-[10px]"
            >
              {impact.sector_name}
            </Badge>
          </div>
        )}
      </div>
    </a>
  );
}
```

- [ ] **Step 3: tsc 확인**

```bash
cd frontend && npx tsc --noEmit
```

- [ ] **Step 4: 커밋**

```bash
git add frontend/src/components/news/ImpactCard.tsx
git commit -m "feat: add ImpactCard with news title, source, and impact score badge"
```

---

## Task 6: NewsImpactFeed (탭 뉴스 피드)

**Files:**
- Create: `frontend/src/components/news/NewsImpactFeed.tsx`

- [ ] **Step 1: NewsImpactFeed 컴포넌트 작성**

```tsx
// frontend/src/components/news/NewsImpactFeed.tsx
import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/utils";
import { ImpactCard } from "./ImpactCard";
import type { NewsArticle, NewsImpactAnalysis } from "@/types";

interface NewsImpactFeedProps {
  articles: NewsArticle[];
  impacts: NewsImpactAnalysis[];
  loading: boolean;
}

const TABS = [
  { key: "all", label: "전체" },
  { key: "business", label: "경제" },
  { key: "technology", label: "기술" },
  { key: "science", label: "과학" },
  { key: "general", label: "글로벌" },
] as const;

export function NewsImpactFeed({ articles, impacts, loading }: NewsImpactFeedProps) {
  const [activeTab, setActiveTab] = useState<string>("all");

  const filteredArticles =
    activeTab === "all"
      ? articles
      : articles.filter((a) => a.category === activeTab);

  const impactMap = new Map(impacts.map((imp) => [imp.news_url, imp]));

  return (
    <Card className="flex h-full flex-col">
      <CardHeader className="pb-2">
        <CardTitle>News Impact Feed</CardTitle>
        <div className="flex gap-1 pt-1">
          {TABS.map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key)}
              className={cn(
                "rounded-md px-2.5 py-1 text-xs font-medium transition-colors",
                activeTab === tab.key
                  ? "bg-foreground/10 text-foreground"
                  : "text-muted-foreground hover:text-foreground",
              )}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </CardHeader>
      <CardContent className="flex-1 space-y-2 overflow-y-auto">
        {loading ? (
          Array.from({ length: 5 }).map((_, i) => (
            <Skeleton key={i} className="h-20 w-full" />
          ))
        ) : filteredArticles.length === 0 ? (
          <p className="py-8 text-center text-sm text-muted-foreground">
            뉴스가 없습니다
          </p>
        ) : (
          filteredArticles.map((article) => (
            <ImpactCard
              key={article.url}
              article={article}
              impact={impactMap.get(article.url)}
            />
          ))
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
git add frontend/src/components/news/NewsImpactFeed.tsx
git commit -m "feat: add NewsImpactFeed with category tabs and impact badges"
```

---

## Task 7: EconomicCalendar (경제 캘린더 위젯)

**Files:**
- Create: `frontend/src/components/news/EconomicCalendar.tsx`

- [ ] **Step 1: EconomicCalendar 컴포넌트 작성**

```tsx
// frontend/src/components/news/EconomicCalendar.tsx
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import type { EconomicIndicator } from "@/types";
import { formatPrice } from "@/lib/utils";
import { cn } from "@/lib/utils";

interface EconomicCalendarProps {
  indicators: EconomicIndicator[];
  loading: boolean;
}

function getDirectionIcon(direction: string): string {
  if (direction === "up") return "▲";
  if (direction === "down") return "▼";
  return "—";
}

function getDirectionColor(direction: string): string {
  if (direction === "up") return "text-bullish";
  if (direction === "down") return "text-bearish";
  return "text-muted-foreground";
}

export function EconomicCalendar({ indicators, loading }: EconomicCalendarProps) {
  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Economic Calendar</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} className="h-10 w-full" />
          ))}
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Economic Calendar</CardTitle>
      </CardHeader>
      <CardContent>
        {indicators.length === 0 ? (
          <p className="py-4 text-center text-sm text-muted-foreground">
            경제 지표 데이터 없음
          </p>
        ) : (
          <div className="space-y-1">
            {indicators.map((ind) => (
              <div
                key={ind.indicator_name}
                className="flex items-center justify-between rounded-lg px-3 py-2 text-sm hover:bg-muted/30"
              >
                <div className="flex items-center gap-2">
                  <span
                    className={cn("text-xs", getDirectionColor(ind.change_direction))}
                  >
                    {getDirectionIcon(ind.change_direction)}
                  </span>
                  <span className="font-medium text-foreground">
                    {ind.indicator_name}
                  </span>
                </div>
                <div className="flex items-center gap-3">
                  <span className="font-mono text-xs text-foreground">
                    {formatPrice(ind.value)}
                  </span>
                  {ind.previous_value !== null && (
                    <span className="font-mono text-xs text-muted-foreground">
                      (prev: {formatPrice(ind.previous_value)})
                    </span>
                  )}
                  <span className="text-xs text-muted-foreground">
                    {new Date(ind.reported_at).toLocaleDateString("ko-KR", {
                      month: "short",
                      day: "numeric",
                    })}
                  </span>
                </div>
              </div>
            ))}
          </div>
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
git add frontend/src/components/news/EconomicCalendar.tsx
git commit -m "feat: add EconomicCalendar widget with indicator list"
```

---

## Task 8: App.tsx — placeholder를 실제 컴포넌트로 교체

**Files:**
- Modify: `frontend/src/App.tsx`

- [ ] **Step 1: App.tsx를 다음으로 교체**

```tsx
// frontend/src/App.tsx
import { useState } from "react";
import { useMarketData } from "@/hooks/useMarketData";
import { useNewsData } from "@/hooks/useNewsData";
import { GlobalMacroHeader } from "@/components/header/GlobalMacroHeader";
import { SectorHeatmap } from "@/components/sector/SectorHeatmap";
import { SectorSparkline } from "@/components/sector/SectorSparkline";
import { MarketMovers } from "@/components/sector/MarketMovers";
import { NewsImpactFeed } from "@/components/news/NewsImpactFeed";
import { EconomicCalendar } from "@/components/news/EconomicCalendar";

export default function App() {
  const marketData = useMarketData();
  const newsData = useNewsData();
  const [selectedSector, setSelectedSector] = useState<string | null>(null);

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
        <div className="space-y-4">
          <SectorHeatmap
            sectors={marketData.sectors}
            loading={marketData.loading}
            onSectorClick={setSelectedSector}
          />
          <SectorSparkline
            sectors={marketData.sectors}
            selectedSector={selectedSector}
            onSectorClick={setSelectedSector}
          />
          <MarketMovers
            sectors={marketData.sectors}
            selectedSector={selectedSector}
          />
        </div>

        {/* Area C: News Impact & Calendar */}
        <div className="space-y-4">
          <NewsImpactFeed
            articles={newsData.articles}
            impacts={newsData.impacts}
            loading={newsData.loading}
          />
          <EconomicCalendar
            indicators={marketData.indicators}
            loading={marketData.loading}
          />
        </div>
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

- [ ] **Step 2: tsc 확인**

```bash
cd frontend && npx tsc --noEmit
```

- [ ] **Step 3: 빌드 확인**

```bash
cd frontend && npm run build
```

Expected: 성공, `dist/` 생성

- [ ] **Step 4: 커밋**

```bash
git add frontend/src/App.tsx
git commit -m "feat: integrate Area B (Sector) and Area C (News) into dashboard layout"
```
