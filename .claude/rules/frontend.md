# Frontend Rules

## TypeScript
- strict mode 필수
- `any` 타입 사용 금지, 공유 타입은 `src/types/index.ts`에 정의
- 서버/클라이언트 컴포넌트 구분 명확히 ("use client" 필요 시에만)

## Vite + React
- Vite + React SPA (CSR 전용, SSR 불필요)
- React Router 사용 (필요 시, 현재는 SPA 단일 페이지)
- 데이터 페칭은 `src/lib/api.ts`의 fetch wrapper 사용
- API 클라이언트는 `src/lib/api.ts`에 중앙��

## UI/Styling
- shadcn/ui 컴포넌트 우선 사용
- Tailwind CSS만 사용 (인라인 스타일, CSS 모듈 금지)
- Dark Mode 기본 (bg-slate-900 계열, 배경 `#0f172a`)
- 색상: 상승 green-500 `#22c55e`, 하락 red-500 `#ef4444`
- 카드(Card) 기반 레이아웃, 데이터 로딩 시 Skeleton UI 적용

## Dashboard Layout (4 Area)
- **Area A (상단):** Global Macro Header — 지수 티커 + 거시 지표(US10Y, DXY, WTI, Gold) + 국면 배지
- **Area B (좌측):** Sector Heatmap & Market Movers — Treemap + Sparklines + 클릭 시 종목 리스트
- **Area C (우측):** News Impact & Calendar — 뉴스 탭(4카테고리) + Impact Score 뱃지 + 경제 캘린더
- **Area D (하단):** Deep Dive Chart & AI Screener — Multi-Chart Grid(2~4분할) + 이벤트 마커 + 스크리너 테이블

## Charts
- **Recharts:** Treemap, GroupedBar, AreaChart, Sparkline
- **TradingView Lightweight Charts (선택):** 인터랙티브 가격 차트 (MA/Volume 토글)
- 반응형 컨테이너(ResponsiveContainer) 필수
- 차트 유형:
  - Grouped Bar: 섹터별 1D/1W/1M 등락률 묶음 막대
  - 52주 Range: Bullet Chart (최저~최고 내 현재 위치)
  - Relative Strength: Baseline Area (S&P500 기준선 0, 초과/하회 채색)
  - Sparkline: 섹터 리스트 내 30일 미니 추세
  - 보조지표: MA, Volume 바 On/Off 토글

## Design Tokens
- 국면 색상: Goldilocks green-500, Reflation amber-500, Stagflation red-500, Deflation blue-500
- Impact Score 뱃지: 1~3 gray, 4~6 amber, 7~10 red

## Component Structure
```
components/
├── header/     # GlobalMacroHeader, TickerBar, RegimeBadge
├── sector/     # SectorHeatmap, SectorSparkline, MarketMovers
├── news/       # NewsImpactFeed, ImpactCard, EconomicCalendar
├── chart/      # MultiChartGrid, PriceChart, RelativeStrength, MomentumBar, RangeChart, EventMarker
├── screener/   # AiScreenerTable
└── ui/         # Skeleton 등 공통 UI
```
