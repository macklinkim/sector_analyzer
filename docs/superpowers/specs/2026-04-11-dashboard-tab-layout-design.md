# Dashboard Tab Layout 분리 설계

**작성일:** 2026-04-11
**상태:** Draft
**적용 범위:** `frontend/src/App.tsx` 및 `frontend/src/components/` 하위

## 1. 배경 & 목적

현재 대시보드는 단일 페이지에 모든 위젯(실제 시장 데이터 + AI 판단 결과)을 Area A/B/C/D 구조로 혼재시켜 배치하고 있다. 사용자가 "지금 시장 상황이 어떤가"(raw data)를 보려는 모드와 "AI가 어떻게 판단했는가"(AI layer)를 보려는 모드의 관심사가 섞여 있어, 화면 스크롤이 길고 두 종류의 정보가 시각적으로 구분되지 않는다.

본 리팩토링의 목적은:

1. 화면을 **2개 탭으로 분리**해 "실제 시장 데이터"와 "AI 판단 결과"의 정보 레이어를 명확히 분리한다.
2. 최상단 `GlobalMacroHeader`(거시 지표 + 국면 배지)는 두 탭에서 공통이므로 **sticky 고정**하여 스크롤과 탭 전환에 관계없이 항상 노출한다.
3. `SectorStockTreemap`을 한 줄 전체 풀폭으로 확장해 구성 종목 라벨의 가독성을 개선한다.
4. 위젯의 의미와 파일 이름/위치의 정합성을 맞춘다 (`BusinessCycleClock` → `chart/`, `MultiChartGrid` → `SectorComparisonCharts`).

## 2. 스코프

### 포함
- 대시보드 루트 레이아웃 (`App.tsx`) 재구성
- 탭 상태 관리 (localStorage 영속)
- 탭 바 UI 컴포넌트 신규 작성
- 2개 탭 컨텐츠 컴포넌트(`MarketTab`, `AiTab`) 신규 작성
- `MultiChartGrid` 내부 구조 단순화 및 `SectorComparisonCharts`로 리네임
- `EventMarker` 경량 래퍼 `AiRotationSignals` 신규 작성
- `BusinessCycleClock` 파일 위치 이동 (`header/` → `chart/`)

### 제외 (YAGNI)
- 탭 전환 애니메이션
- 탭별 lazy data loading
- URL 쿼리 파라미터 탭 동기화
- 3번째 탭(히스토리/설정 등)
- 디렉토리 재구성(위에 명시한 2개 이동 외)
- 기존 위젯 내부 로직 수정

## 3. 아키텍처

### 3.1 컴포넌트 트리

```
<LoginGate>
  <Dashboard>                                       -- App.tsx
    <div className="sticky top-0 z-20 bg-background">
      <GlobalMacroHeader ... />                     -- 변경 없음
      <DashboardTabs activeTab onChange />          -- 신규
    </div>
    <main>
      {activeTab === 'market' && <MarketTab ... />} -- 신규
      {activeTab === 'ai'     && <AiTab ... />}     -- 신규
    </main>
    <footer> ... </footer>                          -- 변경 없음
  </Dashboard>
</LoginGate>
```

### 3.2 상태 관리

- `activeTab: 'market' | 'ai'` — `useStickyState('dashboard_active_tab', 'market')` 훅으로 localStorage 영속
- `selectedSector: string | null` — `Dashboard` 레벨에 유지, 두 탭이 공유
  - 이유: Tab 2 `AiScreenerTable`에서 섹터 클릭 → Tab 1 전환 시 동일 섹터가 선택된 상태로 남아 섹터 드릴다운 경험의 연속성 확보
- 3개 데이터 훅(`useMarketData`, `useNewsData`, `useAnalysisData`)은 `Dashboard` 최상위에서 호출 → 탭 전환 시 재요청 없음 (단일 진실 원천)

### 3.3 탭 전환 전략

조건부 렌더링(`&&`). 비활성 탭은 언마운트 → 차트 인스턴스가 사라져 메모리/리렌더 부담 감소. 데이터는 상위에서 캐시되므로 재마운트 시 추가 네트워크 요청 없이 즉시 재렌더.

## 4. Tab 1: "시장 현황" (Market Tab)

### 4.1 역할
Yahoo Finance 등 외부 API에서 받아온 **실제 시장 데이터 레이어**. AI 추론이나 판단 결과는 포함하지 않는다.

### 4.2 7-Row 레이아웃 (데스크톱 `lg` 기준)

| Row | 폭 | 위젯 | 역할 |
|---|---|---|---|
| 1 | 풀폭 | `SectorHeatmap` | 섹터 Treemap 진입점, 클릭 시 `selectedSector` 설정 |
| 2 | 풀폭 | `SectorStockTreemap` | 선택된 섹터의 구성 종목 Treemap (**요구사항: 풀폭**) |
| 3 | 2열 | `SectorSparkline` \| `MarketMovers` | 섹터 리스트 + 30일 추세 / 섹터 내 상위 종목 top 5 |
| 4 | 2열 | `NewsImpactFeed` \| `EconomicCalendar` | 뉴스 Impact Score 피드 / 경제지표 캘린더 |
| 5 | 풀폭 | `RelativeStrength` | S&P500 대비 상대 강도 Baseline Area |
| 6 | 풀폭 | `MomentumBar` | 섹터별 1D/1W/1M 등락률 Grouped Bar |
| 7 | 풀폭 | `RangeChart` | 섹터별 52주 Range Bullet |

모바일(`grid-cols-1`)에서는 2열 Row가 세로 스택으로 자연 붕괴.

### 4.3 위젯 배치 근거
- Row 1 → Row 2는 "섹터 선택 → 구성 종목 확인"의 자연스러운 드릴다운 경로
- Row 3는 "선택 섹터 관련 상세" 페어(Sparkline + Movers) — 시선 이동 최소화
- Row 4는 이벤트/정보 피드 페어(News + Calendar)
- Row 5~7은 모두 섹터 비교 차트로 가로 공간이 필요 → 풀폭 3스택

## 5. Tab 2: "AI 인사이트" (AI Tab)

### 5.1 역할
AI 파이프라인(LangGraph)이 생성한 **판단/추론 레이어**. 국면 판정, 로테이션 시그널, 섹터 스코어보드.

### 5.2 3-Row 레이아웃 (데스크톱 `lg` 기준)

| Row | 폭 | 위젯 | 역할 |
|---|---|---|---|
| 1 | 2열 | `BusinessCycleClock` \| `RelativeRotationGraph` | 경기 사이클 4국면 좌표 / RRG 2D 좌표 — 맥락 설정 |
| 2 | 풀폭 | `AiRotationSignals` | MAJOR/ALERT/WATCH 등급 카드 리스트 (EventMarker 래퍼) |
| 3 | 풀폭 | `AiScreenerTable` | AI 섹터 스크리너 (점수 + 근거 뉴스) |

### 5.3 정보 계층 (탭 진입 → 인지 순서)

```
① "지금 어느 국면인가?"      → BCC / RRG    (맥락)
② "AI가 무엇을 발견했는가?"  → AI Rotation Signals (판단)
③ "그래서 뭘 봐야 하는가?"    → AiScreenerTable    (실행)
```

공간 배치가 의사결정 흐름과 일치.

## 6. 파일 변경 목록

### 6.1 수정

| 파일 | 변경 내용 |
|---|---|
| `frontend/src/App.tsx` | 탭 상태/탭 바 도입, sticky 래퍼, `MarketTab`/`AiTab` 분기 렌더. 기존 Area B/C/D JSX 제거 |
| `frontend/src/components/chart/MultiChartGrid.tsx` | → `SectorComparisonCharts.tsx`로 **리네임**. `EventMarker` import/렌더 제거, `signals` prop 제거. 내부를 `RelativeStrength` → `MomentumBar` → `RangeChart` 세로 풀폭 스택으로 단순화. Props는 `{ sectors, loading }`만 남김 |

### 6.2 이동

| 파일 | 이동 경로 |
|---|---|
| `frontend/src/components/header/BusinessCycleClock.tsx` | → `frontend/src/components/chart/BusinessCycleClock.tsx` (Tab 2로 이동되므로 "header" 카테고리에서 벗어남. import 경로 전량 갱신) |

### 6.3 신규

| 파일 | 역할 |
|---|---|
| `frontend/src/hooks/useStickyState.ts` | `useState` + `useEffect`로 localStorage 읽기/쓰기 래핑하는 제네릭 훅 (~15줄). JSON.parse 실패 시 initial 값 반환 |
| `frontend/src/components/layout/DashboardTabs.tsx` | 탭 바 컴포넌트. Props: `{ activeTab, onChange }`. Tailwind/shadcn 스타일. `role="tablist"`, `aria-selected` 접근성 |
| `frontend/src/components/layout/MarketTab.tsx` | Tab 1 7-Row 레이아웃 전담. Props: `{ marketData, newsData, selectedSector, setSelectedSector }` |
| `frontend/src/components/layout/AiTab.tsx` | Tab 2 3-Row 레이아웃 전담. Props: `{ marketData, analysisData, selectedSector, setSelectedSector }` |
| `frontend/src/components/chart/AiRotationSignals.tsx` | `EventMarker`를 호출하는 경량 래퍼(~10줄). 향후 AI 시그널 전용 기능(필터/정렬) 확장 포인트. 내부 CardTitle은 이미 "AI Rotation Signals"로 설정되어 있어 추가 수정 불필요 |

### 6.4 변경 없음 (import 경로만 이동)

다음 파일은 내부 로직/Props 변경 없이 import 위치만 `App.tsx`에서 `MarketTab`/`AiTab`로 옮겨진다:

- `header/GlobalMacroHeader.tsx`, `header/TickerBar.tsx`, `header/RegimeBadge.tsx`
- `sector/SectorHeatmap.tsx`, `sector/SectorStockTreemap.tsx`, `sector/SectorSparkline.tsx`, `sector/MarketMovers.tsx`
- `news/NewsImpactFeed.tsx`, `news/EconomicCalendar.tsx`, `news/ImpactCard.tsx`
- `chart/RelativeStrength.tsx`, `chart/MomentumBar.tsx`, `chart/RangeChart.tsx`, `chart/RelativeRotationGraph.tsx`, `chart/EventMarker.tsx`
- `screener/AiScreenerTable.tsx`
- `auth/LoginGate.tsx`

### 6.5 신규 디렉토리

- `frontend/src/components/layout/` — `DashboardTabs.tsx`, `MarketTab.tsx`, `AiTab.tsx`

## 7. 데이터 플로우

```
Dashboard (App.tsx)
├─ useMarketData()     ─┐
├─ useNewsData()        ├─ 최상위에서 단일 호출
├─ useAnalysisData()   ─┘
├─ useStickyState('dashboard_active_tab', 'market')
├─ useState<selectedSector>
│
├─ <sticky>
│  ├─ <GlobalMacroHeader indices indicators regime loading lastUpdated />
│  └─ <DashboardTabs activeTab onChange={setActiveTab} />
│
└─ <main>
   ├─ activeTab='market' → <MarketTab
   │                         marketData newsData
   │                         selectedSector setSelectedSector />
   └─ activeTab='ai'     → <AiTab
                             marketData analysisData
                             selectedSector setSelectedSector />
```

## 8. 타입 정의

```ts
// frontend/src/types/index.ts (기존)에 추가 가능, 또는 인라인
type DashboardTab = 'market' | 'ai';
```

## 9. 접근성

- `DashboardTabs`는 `role="tablist"`, 각 버튼은 `role="tab"` + `aria-selected={active}` + `aria-controls`
- 키보드 이동: Tab 키로 탭 바 포커스 후 Space/Enter로 전환
- 기본 포커스 링 유지 (Tailwind `focus-visible:ring-2`)

## 10. 테스트 전략

프론트엔드 테스트 인프라가 현재 프로젝트에 없으므로(본 리팩토링 범위에서도 도입하지 않음) 수동 검증:

- [ ] Tab 1/Tab 2 전환 시 `selectedSector` 유지
- [ ] 새로고침 후 탭 상태 유지 (localStorage 확인)
- [ ] 스크롤 시 `GlobalMacroHeader` + `DashboardTabs`가 상단 고정
- [ ] `SectorStockTreemap`이 Tab 1에서 풀폭으로 렌더
- [ ] 모바일 뷰포트에서 2열 Row가 세로로 붕괴
- [ ] 차트 로딩 Skeleton 동작
- [ ] 탭 전환 시 차트 언마운트/재마운트 확인 (React DevTools)
- [ ] 빌드 통과 (`npm run build`)

## 11. 롤아웃

배포는 Cloudflare Workers(프론트) + Render(백엔드) 구조이며, 본 변경은 **프론트엔드 단독**이다. 백엔드 API 계약 변경 없음. 정적 빌드 후 Cloudflare 배포로 완료.

## 12. 결정 요약

| # | 결정 | 선택 | 대안 |
|---|---|---|---|
| 1 | 탭 상태 영속 | localStorage (`useStickyState`) | URL 쿼리, 인메모리 |
| 2 | 탭 전환 방식 | 조건부 렌더(`&&`) | `hidden` 스타일 유지 |
| 3 | 탭 이름 | "시장 현황" / "AI 인사이트" | "실시간 시장" / "AI 로테이션", 영문 |
| 4 | MultiChartGrid 처리 | 리팩토링 후 `SectorComparisonCharts`로 리네임 | 파일 유지/해체 |
| 5 | AI Rotation Signals 구현 | `EventMarker`를 호출하는 경량 래퍼 | `EventMarker` 리네임/이동 |
| 6 | BusinessCycleClock 위치 | `chart/`로 이동 | `header/` 유지 |
| 7 | BCC/RRG 배치 | 2열 병치 | 각각 풀폭 세로 |
| 8 | 컴포넌트 공유 state | `Dashboard` 레벨에 `selectedSector` 유지 | 탭별 독립 state |
| 9 | 데이터 페칭 | `Dashboard` 최상위 단일 호출 | 탭별 lazy 호출 |

## 13. 면책 조항

본 리팩토링은 UI 구조/레이아웃에 한정되며, AI 분석 결과/시그널/스코어보드 등 내용 로직은 전혀 변경되지 않는다. "본 분석은 AI의 추론이며, 실제 투자 판단의 근거로 사용할 수 없습니다" 면책 조항은 footer에 그대로 유지된다.
