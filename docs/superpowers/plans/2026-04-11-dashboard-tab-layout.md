# Dashboard Tab Layout Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 기존 단일 페이지 대시보드를 "시장 현황"(실제 시장 데이터)과 "AI 인사이트"(AI 판단) 2개 탭으로 분리하고, 최상단 헤더+탭바를 sticky 고정, `SectorStockTreemap`을 풀폭으로 확장, `MultiChartGrid`→`SectorComparisonCharts` 리네임 및 `BusinessCycleClock`을 `chart/` 디렉토리로 이동한다.

**Architecture:** `useStickyState`(lazy initializer) 훅으로 탭 상태를 localStorage에 영속. 2개 레이아웃 컴포넌트(`MarketTab`, `AiTab`)가 기존 위젯을 래핑. 3개 데이터 훅은 최상위 `Dashboard`에서 단일 호출(단일 진실 원천). 탭 전환은 조건부 렌더(`&&`). 파일 리네임은 `git mv`로 히스토리 보존.

**Tech Stack:** React 19 + TypeScript strict + Vite + Tailwind + shadcn/ui + Recharts. 새 의존성 없음.

**Spec:** `docs/superpowers/specs/2026-04-11-dashboard-tab-layout-design.md`

**Test Strategy:** 본 프로젝트는 프론트엔드 테스트 인프라를 사용하지 않음 (스펙 §10 결정). 검증 게이트는 (1) `npx tsc --noEmit` — 타입 안전성, (2) `npm run build` — 프로덕션 빌드, (3) 스펙 §10의 수동 QA 체크리스트. **jest/vitest 도입 금지**.

---

## File Structure Overview

**Create (5):**
- `frontend/src/hooks/useStickyState.ts`
- `frontend/src/components/layout/DashboardTabs.tsx`
- `frontend/src/components/layout/MarketTab.tsx`
- `frontend/src/components/layout/AiTab.tsx`
- `frontend/src/components/chart/AiRotationSignals.tsx`

**Rename via `git mv` (2):**
- `components/header/BusinessCycleClock.tsx` → `components/chart/BusinessCycleClock.tsx`
- `components/chart/MultiChartGrid.tsx` → `components/chart/SectorComparisonCharts.tsx`

**Modify (3):**
- `frontend/src/types/index.ts` — 인터페이스 추가
- `frontend/src/components/chart/SectorComparisonCharts.tsx` (리네임 후) — EventMarker 제거, 3차트 스택화
- `frontend/src/App.tsx` — 탭 상태, sticky 래퍼, 조건부 렌더로 전면 리팩토링

**Unchanged:** 그 외 모든 컴포넌트/훅/lib 파일

---

## Task 1: types/index.ts에 인터페이스 추가

**Why first:** 이후 모든 레이아웃 컴포넌트 Props가 이 타입을 참조. 훅 반환 형태는 이미 검증 완료 (`useMarketData.ts:8-16`, `useNewsData.ts:8-14`, `useAnalysisData.ts:8-14`).

**Files:**
- Modify: `frontend/src/types/index.ts`

- [ ] **Step 1: types/index.ts 열기**

현재 이 파일에 `MarketIndex`, `Sector`, `EconomicIndicator`, `MacroRegime`, `NewsArticleEnriched`, `NewsImpactAnalysis`, `GlobalCrisis`, `SectorScoreboard`, `RotationSignal`, `MarketReport` 등이 이미 정의되어 있는지 확인. (기존 훅들이 이 파일에서 import 중이므로 존재함.)

- [ ] **Step 2: 파일 하단에 다음 블록 추가**

```ts
// === Dashboard layout types (2026-04-11) ===

export type DashboardTab = 'market' | 'ai';

/**
 * Shape returned by useMarketData(). Layout components import this
 * instead of ReturnType<typeof useMarketData> to avoid coupling
 * layout → hooks direction.
 */
export interface MarketDataState {
  indices: MarketIndex[];
  sectors: Sector[];
  indicators: EconomicIndicator[];
  regime: MacroRegime | null;
  loading: boolean;
  error: string | null;
  lastUpdated: string | null;
  refresh: () => void;
}

export interface NewsDataState {
  articles: NewsArticleEnriched[];
  impacts: NewsImpactAnalysis[];
  crises: GlobalCrisis[];
  loading: boolean;
  error: string | null;
  refresh: () => void;
}

export interface AnalysisDataState {
  scoreboards: SectorScoreboard[];
  signals: RotationSignal[];
  report: MarketReport | null;
  loading: boolean;
  error: string | null;
  refresh: () => void;
}
```

> **주의:** 위 타입 이름들(`MarketIndex`, `Sector`, 등)이 파일에 이미 있는지 확인하고, 있으면 중복 import 없이 같은 파일 내에서 참조 가능. 없으면 import가 필요할 수 있으나 현재 훅들이 이미 이 파일에서 import 중이므로 존재할 가능성이 높음.

- [ ] **Step 3: 타입 체크**

```bash
cd frontend
npx tsc --noEmit
```

Expected: **0 errors** (추가된 타입은 아직 아무도 consume하지 않으므로 영향 없음)

- [ ] **Step 4: 커밋**

```bash
git add src/types/index.ts
git commit -m "feat(types): add DashboardTab and data state interfaces"
```

---

## Task 2: useStickyState 훅 생성

**Files:**
- Create: `frontend/src/hooks/useStickyState.ts`

- [ ] **Step 1: 파일 생성 및 구현**

```ts
import { useEffect, useState } from "react";

/**
 * localStorage에 값을 영속화하는 제네릭 상태 훅.
 *
 * 읽기는 useState의 lazy initializer 패턴을 사용해 첫 페인트에서
 * 올바른 값을 바로 렌더하며, flash of default value를 방지한다.
 * 쓰기는 useEffect에서 JSON.stringify로 동기화한다.
 *
 * CSR-only 프로젝트(Vite SPA)라 SSR 일관성 우려 없음.
 */
export function useStickyState<T>(
  key: string,
  initial: T,
): [T, (value: T) => void] {
  const [value, setValue] = useState<T>(() => {
    try {
      const raw =
        typeof window !== "undefined" ? window.localStorage.getItem(key) : null;
      if (raw == null) return initial;
      return JSON.parse(raw) as T;
    } catch {
      return initial;
    }
  });

  useEffect(() => {
    try {
      window.localStorage.setItem(key, JSON.stringify(value));
    } catch {
      // quota exceeded / disabled — silently ignore
    }
  }, [key, value]);

  return [value, setValue];
}
```

- [ ] **Step 2: 타입 체크**

```bash
cd frontend
npx tsc --noEmit
```

Expected: 0 errors

- [ ] **Step 3: 커밋**

```bash
git add src/hooks/useStickyState.ts
git commit -m "feat(hooks): add useStickyState with lazy initializer"
```

---

## Task 3: BusinessCycleClock을 components/chart/로 이동

**Why:** Tab 2(AI 인사이트)로 이동되면서 `header/` 카테고리에서 벗어남. 의미 정합성 ↑. 스펙 §6.2 기준 import 하는 파일은 `App.tsx` 단 1개 (grep 감사 완료).

**Files:**
- Rename: `frontend/src/components/header/BusinessCycleClock.tsx` → `frontend/src/components/chart/BusinessCycleClock.tsx`
- Modify: `frontend/src/App.tsx` (import 경로)

- [ ] **Step 1: git mv**

```bash
cd frontend
git mv src/components/header/BusinessCycleClock.tsx src/components/chart/BusinessCycleClock.tsx
```

- [ ] **Step 2: App.tsx import 경로 갱신**

`frontend/src/App.tsx`의 다음 줄:
```ts
import { BusinessCycleClock } from "@/components/header/BusinessCycleClock";
```

→ 변경:
```ts
import { BusinessCycleClock } from "@/components/chart/BusinessCycleClock";
```

- [ ] **Step 3: 다른 import 존재 여부 확인 (safety net)**

Grep 툴로 `components/header/BusinessCycleClock` 문자열을 검색. Expected: **0 matches**. 혹시 발견되면 해당 파일도 같이 수정.

- [ ] **Step 4: 타입 체크**

```bash
npx tsc --noEmit
```

Expected: 0 errors

- [ ] **Step 5: 빌드 체크**

```bash
npm run build
```

Expected: 빌드 성공

- [ ] **Step 6: 커밋**

```bash
git add -A
git commit -m "refactor: move BusinessCycleClock to components/chart"
```

---

## Task 4: MultiChartGrid을 SectorComparisonCharts로 리네임 + 단순화

**Files:**
- Rename: `frontend/src/components/chart/MultiChartGrid.tsx` → `frontend/src/components/chart/SectorComparisonCharts.tsx`
- Modify (post-rename): 위 파일 내부 전면 재작성
- Modify: `frontend/src/App.tsx` (import + 사용처)

- [ ] **Step 1: git mv**

```bash
cd frontend
git mv src/components/chart/MultiChartGrid.tsx src/components/chart/SectorComparisonCharts.tsx
```

- [ ] **Step 2: `SectorComparisonCharts.tsx` 전체 내용을 다음으로 교체**

```tsx
import { MomentumBar } from "./MomentumBar";
import { RangeChart } from "./RangeChart";
import { RelativeStrength } from "./RelativeStrength";
import type { Sector } from "@/types";

interface SectorComparisonChartsProps {
  sectors: Sector[];
  loading: boolean;
}

/**
 * Tab 1 "시장 현황"의 섹터 비교 차트 3종을 세로 풀폭 스택으로 렌더한다.
 * 기존 MultiChartGrid에서 EventMarker(AI 시그널)는 제거되어 Tab 2의
 * AiRotationSignals로 분리되었다.
 */
export function SectorComparisonCharts({
  sectors,
  loading,
}: SectorComparisonChartsProps) {
  return (
    <div className="space-y-4">
      <RelativeStrength sectors={sectors} loading={loading} />
      <MomentumBar sectors={sectors} loading={loading} />
      <RangeChart sectors={sectors} loading={loading} />
    </div>
  );
}
```

- [ ] **Step 3: App.tsx에서 일시적으로 빌드 깨짐 방지를 위해 import와 사용처 교체**

`App.tsx`에서:
```ts
import { MultiChartGrid } from "@/components/chart/MultiChartGrid";
```
→
```ts
import { SectorComparisonCharts } from "@/components/chart/SectorComparisonCharts";
```

그리고 JSX 사용처:
```tsx
<MultiChartGrid
  sectors={marketData.sectors}
  signals={analysisData.signals}
  loading={marketData.loading}
/>
```
→
```tsx
<SectorComparisonCharts
  sectors={marketData.sectors}
  loading={marketData.loading}
/>
```

> **주의:** `analysisData.signals`는 Task 9의 AiTab에서 `AiRotationSignals`로 사용됨. 아직 지우지 말 것. `App.tsx`에서 `analysisData` 자체는 계속 유지.

- [ ] **Step 4: 타입 체크**

```bash
npx tsc --noEmit
```

Expected: 0 errors

- [ ] **Step 5: 빌드 체크**

```bash
npm run build
```

Expected: 빌드 성공 (현재 시점의 App.tsx는 여전히 기존 Area 구조를 유지하지만 SectorComparisonCharts 사용하도록 교체됨)

- [ ] **Step 6: 커밋**

```bash
git add -A
git commit -m "refactor: rename MultiChartGrid to SectorComparisonCharts, drop EventMarker"
```

---

## Task 5: AiRotationSignals 래퍼 생성

**Files:**
- Create: `frontend/src/components/chart/AiRotationSignals.tsx`

- [ ] **Step 1: 파일 생성**

```tsx
import { EventMarker } from "./EventMarker";
import type { RotationSignal } from "@/types";

interface AiRotationSignalsProps {
  signals: RotationSignal[];
}

/**
 * Tab 2 "AI 인사이트"의 "AI Rotation Signals" 위젯.
 * 현재는 EventMarker를 그대로 호출하는 경량 래퍼이며,
 * 향후 AI 시그널 전용 기능(필터/정렬/시간 범위)을 추가할 확장 포인트.
 *
 * EventMarker 내부의 CardTitle은 이미 "AI Rotation Signals"로
 * 설정되어 있으므로 추가 수정 불필요 (verified 2026-04-11).
 */
export function AiRotationSignals({ signals }: AiRotationSignalsProps) {
  return <EventMarker signals={signals} />;
}
```

- [ ] **Step 2: 타입 체크**

```bash
npx tsc --noEmit
```

Expected: 0 errors

- [ ] **Step 3: 커밋**

```bash
git add src/components/chart/AiRotationSignals.tsx
git commit -m "feat(chart): add AiRotationSignals wrapper for Tab 2"
```

---

## Task 6: DashboardTabs 탭바 컴포넌트 생성

**Files:**
- Create: `frontend/src/components/layout/DashboardTabs.tsx`

- [ ] **Step 1: 디렉토리 생성 확인 + 파일 작성**

Note: `frontend/src/components/layout/` 디렉토리는 신규. 파일을 만들면 자동 생성됨.

```tsx
import type { DashboardTab } from "@/types";
import { cn } from "@/lib/utils";

interface DashboardTabsProps {
  activeTab: DashboardTab;
  onChange: (tab: DashboardTab) => void;
}

interface TabDef {
  id: DashboardTab;
  label: string;
}

const TABS: TabDef[] = [
  { id: "market", label: "시장 현황" },
  { id: "ai", label: "AI 인사이트" },
];

export function DashboardTabs({ activeTab, onChange }: DashboardTabsProps) {
  return (
    <div
      role="tablist"
      aria-label="대시보드 탭"
      className="flex gap-1 border-b border-border bg-background px-4"
    >
      {TABS.map((tab) => {
        const active = tab.id === activeTab;
        return (
          <button
            key={tab.id}
            type="button"
            role="tab"
            id={`tab-${tab.id}`}
            aria-selected={active}
            aria-controls={`panel-${tab.id}`}
            onClick={() => onChange(tab.id)}
            className={cn(
              "relative px-4 py-3 text-sm font-medium transition-colors",
              "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2",
              active
                ? "text-foreground"
                : "text-muted-foreground hover:text-foreground",
            )}
          >
            {tab.label}
            {active && (
              <span
                aria-hidden="true"
                className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary"
              />
            )}
          </button>
        );
      })}
    </div>
  );
}
```

- [ ] **Step 2: 타입 체크**

```bash
npx tsc --noEmit
```

Expected: 0 errors. (`cn` 유틸과 `DashboardTab` 타입은 기존 경로에서 resolve됨)

- [ ] **Step 3: 커밋**

```bash
git add src/components/layout/DashboardTabs.tsx
git commit -m "feat(layout): add DashboardTabs bar with a11y attributes"
```

---

## Task 7: MarketTab 패널 컴포넌트 생성

**Files:**
- Create: `frontend/src/components/layout/MarketTab.tsx`

- [ ] **Step 1: 파일 작성 — 스펙 §4.2의 7-Row 레이아웃 구현**

```tsx
import { SectorComparisonCharts } from "@/components/chart/SectorComparisonCharts";
import { EconomicCalendar } from "@/components/news/EconomicCalendar";
import { NewsImpactFeed } from "@/components/news/NewsImpactFeed";
import { MarketMovers } from "@/components/sector/MarketMovers";
import { SectorHeatmap } from "@/components/sector/SectorHeatmap";
import { SectorSparkline } from "@/components/sector/SectorSparkline";
import { SectorStockTreemap } from "@/components/sector/SectorStockTreemap";
import type { MarketDataState, NewsDataState } from "@/types";

interface MarketTabProps {
  marketData: MarketDataState;
  newsData: NewsDataState;
  selectedSector: string | null;
  setSelectedSector: (sector: string | null) => void;
}

export function MarketTab({
  marketData,
  newsData,
  selectedSector,
  setSelectedSector,
}: MarketTabProps) {
  const selectedEtf =
    marketData.sectors.find((s) => s.name === selectedSector)?.etf_symbol ??
    null;

  return (
    <div
      id="panel-market"
      role="tabpanel"
      aria-labelledby="tab-market"
      className="space-y-4 p-4"
    >
      {/* Row 1: SectorHeatmap (풀폭) */}
      <SectorHeatmap
        sectors={marketData.sectors}
        loading={marketData.loading}
        onSectorClick={setSelectedSector}
      />

      {/* Row 2: SectorStockTreemap — 풀폭 (요구사항) */}
      <SectorStockTreemap
        selectedSector={selectedSector}
        etfSymbol={selectedEtf}
      />

      {/* Row 3: Sparkline + MarketMovers (2열) */}
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
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

      {/* Row 4: News + Calendar (2열) */}
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <NewsImpactFeed
          articles={newsData.articles}
          impacts={newsData.impacts}
          crises={newsData.crises}
          loading={newsData.loading}
        />
        <EconomicCalendar
          indicators={marketData.indicators}
          loading={marketData.loading}
        />
      </div>

      {/* Row 5~7: 섹터 비교 차트 스택 (RS, MB, RC) */}
      <SectorComparisonCharts
        sectors={marketData.sectors}
        loading={marketData.loading}
      />
    </div>
  );
}
```

- [ ] **Step 2: 타입 체크**

```bash
npx tsc --noEmit
```

Expected: 0 errors. (`MarketTab`은 아직 import되지 않지만 컴파일은 성공해야 함)

- [ ] **Step 3: 커밋**

```bash
git add src/components/layout/MarketTab.tsx
git commit -m "feat(layout): add MarketTab panel with 7-row real-data layout"
```

---

## Task 8: AiTab 패널 컴포넌트 생성

**Files:**
- Create: `frontend/src/components/layout/AiTab.tsx`

- [ ] **Step 1: 파일 작성 — 스펙 §5.2의 3-Row 레이아웃 구현**

```tsx
import { AiRotationSignals } from "@/components/chart/AiRotationSignals";
import { BusinessCycleClock } from "@/components/chart/BusinessCycleClock";
import { RelativeRotationGraph } from "@/components/chart/RelativeRotationGraph";
import { AiScreenerTable } from "@/components/screener/AiScreenerTable";
import type { AnalysisDataState, MarketDataState } from "@/types";

interface AiTabProps {
  marketData: MarketDataState;
  analysisData: AnalysisDataState;
  selectedSector: string | null;
  setSelectedSector: (sector: string | null) => void;
}

export function AiTab({
  marketData,
  analysisData,
  selectedSector,
  setSelectedSector,
}: AiTabProps) {
  return (
    <div
      id="panel-ai"
      role="tabpanel"
      aria-labelledby="tab-ai"
      className="space-y-4 p-4"
    >
      {/* Row 1: BCC + RRG (2열) — 맥락 설정 */}
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <BusinessCycleClock
          regime={marketData.regime}
          loading={marketData.loading}
        />
        <RelativeRotationGraph
          sectors={marketData.sectors}
          loading={marketData.loading}
        />
      </div>

      {/* Row 2: AI Rotation Signals (풀폭) — 판단 */}
      <AiRotationSignals signals={analysisData.signals} />

      {/* Row 3: AI Sector Screener (풀폭) — 실행 */}
      <AiScreenerTable
        scoreboards={analysisData.scoreboards}
        loading={analysisData.loading}
        selectedSector={selectedSector}
        onSectorClick={setSelectedSector}
      />
    </div>
  );
}
```

- [ ] **Step 2: 타입 체크**

```bash
npx tsc --noEmit
```

Expected: 0 errors

- [ ] **Step 3: 커밋**

```bash
git add src/components/layout/AiTab.tsx
git commit -m "feat(layout): add AiTab panel with 3-row AI insights layout"
```

---

## Task 9: App.tsx 전면 리팩토링 — sticky 헤더 + 탭 분기

**Files:**
- Modify: `frontend/src/App.tsx`

**Why last:** 이 작업이 실제로 탭 구조를 활성화한다. 이전 Task에서 만들어진 모든 부품(훅, 타입, 탭바, 탭 패널)이 여기서 조립된다.

- [ ] **Step 1: App.tsx 전체 교체**

```tsx
import { useState } from "react";
import { LoginGate, logout, useAuth } from "@/components/auth/LoginGate";
import { GlobalMacroHeader } from "@/components/header/GlobalMacroHeader";
import { AiTab } from "@/components/layout/AiTab";
import { DashboardTabs } from "@/components/layout/DashboardTabs";
import { MarketTab } from "@/components/layout/MarketTab";
import { useAnalysisData } from "@/hooks/useAnalysisData";
import { useMarketData } from "@/hooks/useMarketData";
import { useNewsData } from "@/hooks/useNewsData";
import { useStickyState } from "@/hooks/useStickyState";
import type { DashboardTab } from "@/types";

function Dashboard() {
  const { name } = useAuth();
  const marketData = useMarketData();
  const newsData = useNewsData();
  const analysisData = useAnalysisData();
  const [activeTab, setActiveTab] = useStickyState<DashboardTab>(
    "dashboard_active_tab",
    "market",
  );
  const [selectedSector, setSelectedSector] = useState<string | null>(null);

  return (
    <div className="min-h-screen bg-background text-foreground">
      {/* Sticky top: GlobalMacroHeader + DashboardTabs */}
      <div className="sticky top-0 z-40 bg-background">
        <header>
          <GlobalMacroHeader
            indices={marketData.indices}
            indicators={marketData.indicators}
            regime={marketData.regime}
            loading={marketData.loading}
            lastUpdated={marketData.lastUpdated}
          />
        </header>
        <DashboardTabs activeTab={activeTab} onChange={setActiveTab} />
      </div>

      <main>
        {activeTab === "market" && (
          <MarketTab
            marketData={marketData}
            newsData={newsData}
            selectedSector={selectedSector}
            setSelectedSector={setSelectedSector}
          />
        )}
        {activeTab === "ai" && (
          <AiTab
            marketData={marketData}
            analysisData={analysisData}
            selectedSector={selectedSector}
            setSelectedSector={setSelectedSector}
          />
        )}
      </main>

      <footer className="border-t border-border px-4 py-3">
        <div className="flex items-center justify-between">
          <span className="text-xs text-muted-foreground">
            본 분석은 AI의 추론이며, 실제 투자 판단의 근거로 사용할 수 없습니다.
          </span>
          <div className="flex items-center gap-3">
            <span className="text-xs text-muted-foreground">{name}</span>
            <button
              type="button"
              onClick={logout}
              className="text-xs text-muted-foreground underline hover:text-foreground"
            >
              로그아웃
            </button>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default function App() {
  return (
    <LoginGate>
      <Dashboard />
    </LoginGate>
  );
}
```

- [ ] **Step 2: 타입 체크**

```bash
npx tsc --noEmit
```

Expected: **0 errors**. 훅 반환 형태가 `MarketDataState`/`NewsDataState`/`AnalysisDataState` 인터페이스와 구조적으로 호환되어야 함 — Task 1에서 실제 훅 형태 기준으로 인터페이스를 정의했으므로 정합해야 정상.

**만약 타입 에러가 나면:**
- 에러 메시지를 읽고 실제 훅 반환 형태와 인터페이스의 차이 확인
- **원칙: 훅이 source of truth**. 훅은 수정하지 말고 `types/index.ts`의 인터페이스를 훅 반환 형태에 맞춰 수정
- 수정 후 재실행

- [ ] **Step 3: 빌드 체크**

```bash
npm run build
```

Expected: 빌드 성공, `dist/` 생성

- [ ] **Step 4: 커밋**

```bash
git add src/App.tsx
git commit -m "refactor(app): split dashboard into market/ai tabs with sticky header"
```

**선택: 인터페이스 수정이 필요했다면 별도 커밋**

```bash
git add src/types/index.ts
git commit -m "fix(types): align data state interfaces with actual hook shapes"
```

---

## Task 10: 수동 QA (스펙 §10 체크리스트)

**Files:** 없음 (검증 only)

- [ ] **Step 1: 개발 서버 시작**

```bash
cd frontend
npm run dev
```

브라우저에서 http://localhost:5173 접속 후 로그인.

- [ ] **Step 2: Tab 1 "시장 현황" 기본 렌더 확인**
  - 7-Row 레이아웃이 보이는가
  - Row 2 `SectorStockTreemap`이 **풀폭**인가 (한 줄 전체 차지)
  - Row 3이 2열(Sparkline + MarketMovers)인가
  - Row 4가 2열(News + Calendar)인가
  - Row 5~7이 풀폭 세로 스택(RelativeStrength → MomentumBar → RangeChart)인가

- [ ] **Step 3: selectedSector 연동**
  - `SectorHeatmap`의 섹터 하나 클릭 → Row 2 Treemap이 해당 섹터 구성 종목 표시
  - 동일 클릭이 Row 3 `MarketMovers`에도 반영

- [ ] **Step 4: Tab 2 "AI 인사이트" 전환**
  - DashboardTabs의 "AI 인사이트" 클릭
  - Row 1에 BCC + RRG가 2열로 나란히
  - Row 2 AI Rotation Signals 풀폭
  - Row 3 AiScreenerTable 풀폭

- [ ] **Step 5: 탭 간 selectedSector 공유**
  - Tab 2의 `AiScreenerTable`에서 섹터 행 클릭
  - Tab 1로 다시 전환 → 동일 섹터가 선택된 상태가 유지되는지 확인

- [ ] **Step 6: Sticky 헤더**
  - 아무 탭에서나 아래로 스크롤
  - `GlobalMacroHeader` + `DashboardTabs`가 상단에 고정되는지 확인

- [ ] **Step 7: z-index 계층**
  - `SectorHeatmap` Treemap 위에 마우스 호버 → Recharts tooltip이 sticky 헤더에 의해 **잘리지 않고** 보이는지 확인
  - `RangeChart` Bullet에도 동일 확인
  - 만약 tooltip이 헤더 아래로 숨으면 → (a) tooltip `wrapperStyle`에 `zIndex: 60` 설정, 또는 (b) sticky 헤더 `z-40` 유지하되 문제 차트 컨테이너에 `isolation: isolate` 추가. 해결 후 해당 수정을 커밋.

- [ ] **Step 8: 로그인 모달 오버레이**
  - 로그아웃 후 재로그인 → `LoadingScreen`(z-50)이 sticky 헤더 위에 정상 오버레이

- [ ] **Step 9: localStorage 영속성**
  - DevTools > Application > Local Storage > `dashboard_active_tab` 키 확인
  - 값이 `"market"` 또는 `"ai"`로 저장되는지
  - 수동으로 `"ai"`로 설정 후 페이지 새로고침
  - **Tab 1이 먼저 보였다가 Tab 2로 바뀌는 flash가 없는지** 확인 (lazy initializer 검증)

- [ ] **Step 10: 모바일 뷰포트**
  - DevTools 반응형 모드 → 375px 너비
  - 2열 Row가 세로 스택으로 자연 붕괴

- [ ] **Step 11: 키보드 접근성**
  - Tab 키로 `DashboardTabs` 버튼에 포커스 이동
  - Space 또는 Enter로 탭 전환
  - focus ring이 시각적으로 보이는지

- [ ] **Step 12: 프로덕션 빌드**

```bash
npm run build
```

Expected: 빌드 성공. dist/ 산출물 생성.

- [ ] **Step 13: QA 수정 (필요 시)**

위 Step들 중 실패한 항목이 있으면 수정하고 개별 fix 커밋으로 처리. 예:

```bash
git add -A
git commit -m "fix(layout): raise Recharts tooltip z-index above sticky header"
```

---

## Rollout Notes

- **스코프:** 프론트엔드 단독. 백엔드 API 계약 변경 없음.
- **배포 대상:** Cloudflare Workers (프론트). 백엔드 재배포 불필요.
- **되돌리기:** 모든 변경은 커밋 단위로 분리되어 있어 Task 단위 revert 가능. 최악의 경우 전체 `git revert <마지막 커밋>..<첫 커밋>` 또는 브랜치 리셋.
- **사용자 영향:** 기존 사용자는 첫 접속 시 localStorage에 키가 없으므로 기본값 "시장 현황" 탭으로 진입. 브레이킹 체인지 없음.
- **후속 과제 (스펙 범위 외):**
  - 탭 전환 빈도가 높다는 피드백이 나오면 `hidden` 스타일 기반(항상 마운트)으로 전환 검토
  - AI Rotation Signals 위젯에 필터/정렬/시간 범위 기능 추가 (확장 포인트 활용)
