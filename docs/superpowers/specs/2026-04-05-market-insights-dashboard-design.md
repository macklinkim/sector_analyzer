# Design Spec: AI-Driven Market Insights Dashboard (Sector Rotation)

**Date:** 2026-04-05
**Status:** Approved
**Purpose:** 시장의 섹터 순환매(Sector Rotation) 흐름을 선제적으로 포착하고 투자 인사이트를 제공하는 종합 미국 주식 대시보드

---

## 1. 의사결정 요약

| 항목 | 결정 |
| :--- | :--- |
| 에이전트 프레임워크 | LangGraph |
| AI 모델 | Claude API |
| 금융 데이터 | EODHD API (발급 필요) |
| 뉴스 데이터 | NewsAPI.org (발급 필요) + Google News RSS (Fallback) |
| DB | Supabase |
| 아키텍처 | Monorepo (backend + frontend) |
| 프론트엔드 | Vite + React SPA (Next.js 제외 — FastAPI 단일 배포 우선) |
| 배포 | Railway/Render 단일 배포 (FastAPI가 SPA 서빙) 또는 정적 분리 배포 |
| Google 연동 | 2차 개발 (후순위) |
| 스케줄 | 1일 2회 (Pre-Market 08:30 ET, Post-Market 17:00 ET) |
| 심화 스크래핑 | Playwright MCP (동적 웹페이지 데이터 수집) |

---

## 2. 프로젝트 구조

```
economi_analyzer/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI 앱 진입점
│   │   ├── config.py            # 환경변수, API 키 관리
│   │   ├── api/
│   │   │   ├── routes/
│   │   │   │   ├── market.py    # 섹터/지수 데이터 엔드포인트
│   │   │   │   ├── news.py      # 뉴스 + Impact Score 엔드포인트
│   │   │   │   └── analysis.py  # AI 분석 리포트 엔드포인트
│   │   │   └── deps.py          # 공통 의존성
│   │   ├── agents/
│   │   │   ├── graph.py         # LangGraph 메인 그래프 정의
│   │   │   ├── state.py         # 그래프 공유 상태 스키마
│   │   │   ├── data_agent.py    # EODHD 데이터 수집 노드
│   │   │   ├── news_agent.py    # 뉴스 수집 노드
│   │   │   └── analyst_agent.py # Claude 기반 분석 노드
│   │   ├── mcp/
│   │   │   ├── news_server.py   # NewsAPI MCP 서버
│   │   │   └── playwright_tasks.py # Playwright MCP 스크래핑 태스크 정의
│   │   ├── models/
│   │   │   ├── market.py        # 섹터/지수 스키마
│   │   │   ├── news.py          # 뉴스 스키마
│   │   │   └── analysis.py      # 분석 결과 스키마
│   │   ├── services/
│   │   │   ├── eodhd.py         # EODHD API 클라이언트
│   │   │   ├── newsapi.py       # NewsAPI 클라이언트
│   │   │   ├── rss_fallback.py  # Google News RSS 폴백
│   │   │   └── supabase.py      # Supabase 클라이언트
│   │   └── scheduler/
│   │       └── jobs.py          # APScheduler 배치 작업
│   ├── tests/
│   ├── pyproject.toml
│   └── .env.example
├── frontend/                                    # Vite + React SPA
│   ├── src/
│   │   ├── App.tsx                           # 루트 컴포넌트 (4 Area 그리드)
│   │   ├── main.tsx                          # Vite 진입점
│   │   ├── index.css                         # Tailwind + Dark Mode
│   │   ├── components/
│   │   │   ├── header/
│   │   │   │   ├── GlobalMacroHeader.tsx     # Area A: 전체 헤더
│   │   │   │   ├── TickerBar.tsx             # 지수 + 거시지표 횡렬 티커
│   │   │   │   └── RegimeBadge.tsx           # 현재 국면 배지
│   │   │   ├── sector/
│   │   │   │   ├── SectorHeatmap.tsx         # Area B: Treemap/Grid 히트맵
│   │   │   │   ├── SectorSparkline.tsx       # 리스트 뷰 + 30일 스파크라인
│   │   │   │   └── MarketMovers.tsx          # 섹터 내 급등/급락/거래량 Top5
│   │   │   ├── news/
│   │   │   │   ├── NewsImpactFeed.tsx        # Area C: 탭 뉴스 피드
│   │   │   │   ├── ImpactCard.tsx            # 뉴스 카드 + Impact Score 뱃지
│   │   │   │   └── EconomicCalendar.tsx      # 경제 캘린더 위젯
│   │   │   ├── chart/
│   │   │   │   ├── MultiChartGrid.tsx        # Area D: 2~4분할 차트 컨테이너
│   │   │   │   ├── PriceChart.tsx            # 가격 차트 + MA/Vol 토글
│   │   │   │   ├── RelativeStrength.tsx      # Baseline Area (S&P500 기준)
│   │   │   │   ├── MomentumBar.tsx           # Grouped Bar (1D/1W/1M)
│   │   │   │   ├── RangeChart.tsx            # 52주 Bullet Chart
│   │   │   │   └── EventMarker.tsx           # AI 이벤트 마커 오버레이
│   │   │   ├── screener/
│   │   │   │   └── AiScreenerTable.tsx       # AI Top Picks 테이블
│   │   │   └── ui/
│   │   │       └── Skeleton.tsx              # 스켈레톤 로딩
│   │   ├── lib/
│   │   │   ├── api.ts
│   │   │   └── utils.ts
│   │   └── types/index.ts
│   ├── vite.config.ts
│   ├── tailwind.config.ts
│   ├── tsconfig.json
│   └── package.json
├── docs/
│   ├── draft.md
│   └── sector-rotation-strategy.md
├── CLAUDE.md
└── AGENTS.md
```

---

## 3. 핵심 아키텍처

### 데이터 플로우

```
[Scheduler: 08:30 ET / 17:00 ET]
    │
    ▼
[Data Agent] ──EODHD API──▶ 섹터/지수 데이터 + 모멘텀 계산
    │                        경제 지표 수집
    ▼
[News Agent] ──NewsAPI MCP──▶ 정치/경제/사회/글로벌 뉴스 3건씩 (Fast Track)
    │         ──Fetch MCP──▶ 뉴스 원문 마크다운 변환
    │         (Fallback: Google News RSS)
    │
[Data Agent] ──Playwright MCP──▶ 동적 금융 포털 데이터 수집 (Heavy Track)
    │         ──Claude Vision──▶ 차트/히트맵 스크린샷 분석
    ▼
[Analyst Agent] ──Claude API──▶ 4단계 판단 프로세스
    │  Step 1: 매크로 국면 감지 (Regime Detection)
    │  Step 2: 기본 점수 할당 (Base Score)
    │  Step 3: 가중치 보정 (Override Adjustment)
    │  Step 4: 최종 리포팅 (Sector Scoreboard)
    ▼
[Supabase] ◄── 전체 분석 결과 저장
    │
    ▼
[FastAPI REST API] ──▶ [Next.js Dashboard]
```

### LangGraph 그래프 구조

```python
# 노드: data_agent → news_agent → analyst_agent
# 상태: MarketAnalysisState (TypedDict)
# 조건부 엣지: NewsAPI 실패 시 → rss_fallback 노드
```

---

## 4. 데이터 모델

상세 스키마는 본 문서 Section 4에 정의. 핵심 테이블:

- **market_indices**: 주요 지수 (S&P500, NASDAQ, DOW)
- **sectors**: 섹터별 데이터 + 모멘텀 + 상대강도
- **economic_indicators**: 핵심 경제 지표 히스토리
- **macro_regimes**: 거시 경제 국면 판단 (2D 매트릭스)
- **sector_regime_mapping**: 섹터-국면 매핑 + Override 규칙 (참조 테이블)
- **news_articles**: 수집된 뉴스
- **news_impact_analyses**: 뉴스별 섹터 영향 분석
- **rotation_signals**: 순환매 신호
- **sector_scoreboards**: 섹터별 종합 점수 (배치마다 생성)
- **market_reports**: 종합 리포트

섹터 로테이션 전략 상세: `docs/sector-rotation-strategy.md` 참조

---

## 5. 프론트엔드 대시보드 레이아웃

### 5.1 전체 레이아웃 (SPA, 4개 Area)

```
┌──────────────────────────────────────────────────────────┐
│  [A] Global Macro Header                                  │
│  S&P500 +0.5% │ NASDAQ +0.8% │ DOW +0.3%                │
│  US10Y 4.25%  │ DXY 104.2    │ WTI $78.5 │ Gold $2320   │
│  현재 국면: Goldilocks (60%)   갱신: 08:30 ET  AI분석중... │
├─────────────────────────┬────────────────────────────────┤
│  [B] Sector Heatmap     │  [C] News Impact & Calendar     │
│  & Market Movers        │                                 │
│                         │  뉴스 탭 [정치|경제|사회|글로벌]   │
│  Treemap/Grid           │  뉴스카드 + Impact Score 뱃지    │
│  + 30일 Sparklines      │                                 │
│                         │  ─────────────────────────      │
│  클릭 시 →              │  경제 캘린더 위젯                 │
│  Market Movers 리스트   │  (CPI, FOMC 등 이번주 일정)      │
│  (급등/급락/거래량 Top5) │                                 │
├─────────────────────────┴────────────────────────────────┤
│  [D] Interactive Deep Dive & AI Screener                  │
│                                                           │
│  Multi-Chart Grid (2~4분할)                               │
│  ┌─────────────┬─────────────┐                           │
│  │ 지수 차트    │ 섹터 차트    │  + AI 이벤트 마커 오버레이 │
│  │ +MA/Vol 토글 │ +상대강도    │  + 52주 레인지 Bullet     │
│  └─────────────┴─────────────┘                           │
│                                                           │
│  AI Top Picks Screener Table (확장 패널)                   │
│  티커 │ 종목명 │ AI점수 │ PER │ ROE │ FCF │ 1M등락률      │
└──────────────────────────────────────────────────────────┘
```

### 5.2 Area별 상세

**Area A: Global Macro Header**
- 실시간 티커 바: 주요 지수(S&P500, NASDAQ, DOW) + 거시 지표(US 10Y, DXY, WTI, Gold) 횡렬 배치
- 상태 표시: 마지막 갱신 시간 + AI 분석 진행 상태
- 현재 매크로 국면 배지 (Goldilocks/Reflation/Stagflation/Deflation + 확률%)

**Area B: Sector Heatmap & Market Movers**
- 섹터 히트맵: 11개 섹터 등락률을 Treemap 또는 Grid로 시각화 (크기=시가총액, 색상=등락률)
- 스파크라인: 리스트 뷰에서 각 섹터 옆 최근 30일 미니 선형 차트
- Market Movers: 섹터 클릭 시 하단에 해당 섹터 내 급등주/급락주/최다거래량 Top 5 리스트 전환

**Area C: News Impact & Macro Calendar**
- AI 뉴스 피드: 정치/경제/사회/글로벌 탭, Impact Score(1~10) 뱃지
- 경제 캘린더 위젯: 이번 주 핵심 지표 발표 일정 (CPI, FOMC 등) 미니 달력/타임라인

**Area D: Interactive Deep Dive & AI Screener**
- Multi-Chart Grid: 화면 2~4분할, 지수/섹터/거시지표 동시 렌더링
- AI 이벤트 마커: 차트 X축에 경제 지표 발표일/핵심 뉴스 시점 아이콘 오버레이 (클릭 시 툴팁)
- AI Top Picks 스크리너: 현재 매크로 국면 기반 최우선 종목 테이블 (티커, AI점수, PER, ROE, FCF, 1M등락률)

### 5.3 차트 컴포넌트 상세 요구사항

| 차트 유형 | 용도 | 구현 |
|-----------|------|------|
| **Grouped Bar** | 섹터별 1D/1W/1M 등락률 비교 | 묶음 막대형 |
| **52주 Range (Bullet)** | 52주 최저~최고 내 현재 위치 표시 | Bullet Chart |
| **Relative Strength (Baseline Area)** | S&P500 대비 섹터 초과/하회 수익 | Area Chart (0선 기준 채색) |
| **Treemap** | 섹터 히트맵 (크기=시총, 색=등락률) | Recharts Treemap |
| **Sparkline** | 섹터 리스트 내 30일 미니 추세 | 미니 Line Chart |
| **보조지표 오버레이** | MA(이동평균), Volume 바 On/Off 토글 | 차트 위젯 내 토글 컨트롤 |

### 5.4 컴포넌트 트리

```
frontend/src/
├── App.tsx                     # 루트 컴포넌트 (4 Area 그리드)
├── main.tsx                    # Vite 진입점
├── index.css                   # Tailwind + 커스텀 변수 (Dark Mode)
├── components/
│   ├── header/
│   │   ├── GlobalMacroHeader.tsx   # Area A: 티커 바 + 거시 지표
│   │   ├── TickerBar.tsx           # 지수/거시 지표 횡렬 티커
│   │   └── RegimeBadge.tsx         # 현재 국면 배지
│   ├── sector/
│   │   ├── SectorHeatmap.tsx       # Area B: Treemap/Grid 히트맵
│   │   ├── SectorSparkline.tsx     # 리스트 뷰 + 30일 스파크라인
│   │   └── MarketMovers.tsx        # 섹터 내 급등/급락/거래량 Top5
│   ├── news/
│   │   ├── NewsImpactFeed.tsx      # Area C: 탭 뉴스 피드
│   │   ├── ImpactCard.tsx          # 뉴스 카드 + Impact Score 뱃지
│   │   └── EconomicCalendar.tsx    # 경제 캘린더 위젯
│   ├── chart/
│   │   ├── MultiChartGrid.tsx      # Area D: 2~4분할 차트 컨테이너
│   │   ├── PriceChart.tsx          # 가격 차트 + MA/Vol 토글
│   │   ├── RelativeStrength.tsx    # Baseline Area (S&P500 기준)
│   │   ├── MomentumBar.tsx         # Grouped Bar (1D/1W/1M)
│   │   ├── RangeChart.tsx          # 52주 Bullet Chart
│   │   └── EventMarker.tsx         # AI 이벤트 마커 오버레이
│   ├── screener/
│   │   └── AiScreenerTable.tsx     # AI Top Picks 테이블
│   └── ui/
│       └── Skeleton.tsx            # 스켈레톤 로딩
├── lib/
│   ├── api.ts                  # FastAPI 클라이언트
│   └── utils.ts                # 포맷터, 색상 헬퍼
└── types/
    └── index.ts                # 공유 타입
```

---

## 6. 디자인 가이드

- **테마:** Dark Mode 기본
- **배경:** `#0f172a` (딥 그레이/블랙)
- **색상 팔레트:**
  - 상승(Bullish): `#22c55e` (Green)
  - 하락(Bearish): `#ef4444` (Red)
  - 텍스트: White + 밝은 Gray
- **국면 색상:** Goldilocks `#22c55e`, Reflation `#f59e0b`, Stagflation `#ef4444`, Deflation `#3b82f6`
- **UI 원칙:** 카드(Card) 레이아웃, Skeleton UI 로딩, 반응형
- **차트 라이브러리:** Recharts 기본 + TradingView Lightweight Charts (인터랙티브 가격 차트용 선택)
- **컴포넌트:** shadcn/ui 기반, Tailwind CSS

---

## 7. 제약사항

- NewsAPI 무료 100회/일 → 배치 캐싱 + RSS fallback
- EODHD API 호출 제한 관리
- AI Hallucination → 프롬프트 튜닝 + Harness 검증
- 배치 처리 지연 (수 분) → 실시간이 아닌 갱신 시점 표시
- **면책 조항 필수:** AI 추론이며 투자 지표로 사용 불가

### Playwright MCP 관련 제약사항

- **리소스 및 지연 시간 (Latency) 증가:** Playwright MCP를 통한 실제 브라우저 렌더링은 일반 API 호출(`fetch`)보다 처리 시간(수 초~수십 초)이 훨씬 길다. 시스템 부하를 막기 위해 가벼운 정보는 NewsAPI(Fast Track)로, 복잡한 동적 데이터 및 화면 캡처는 Playwright(Heavy Track)로 **에이전트의 도구 사용을 엄격히 이원화**한다.
- **Bot 탐지 차단 방어 (Anti-Scraping):** 대형 금융 사이트는 Cloudflare 등 강력한 봇 방어 솔루션을 사용한다. Headless 브라우저 접근이 차단될 위험이 있으므로, 프록시(Proxy) IP 라우팅이나 Stealth 플러그인 등 백엔드 차원의 우회 전략 설계가 필요할 수 있다.

---

## 8. 개발 단계 (Phase)

### Phase 1: 기반 구축
- 프로젝트 스캐폴딩, 환경 설정
- Supabase 테이블 생성, API 키 발급
- EODHD / NewsAPI 클라이언트 구현

### Phase 2: AI 파이프라인
- LangGraph 그래프 + 3개 에이전트 구현
- NewsAPI MCP 서버 구축
- Analyst Agent 4단계 판단 로직 구현

### Phase 3: API + 스케줄러
- FastAPI 엔드포인트 구현
- APScheduler 배치 작업 설정

### Phase 4: 프론트엔드
- Vite + React SPA + shadcn/ui 대시보드 구현
- 4 Area 레이아웃, 차트, 히트맵, 뉴스 피드, 스크리너 컴포넌트

### Phase 5: 통합 + 배포
- E2E 통합 테스트
- Railway/Render 단일 배포 (FastAPI가 SPA 정적 파일 서빙)
- 면책 조항, 모니터링

### Phase 6 (후순위): Google 연동
- Google Sheets 누적 저장
- Gmail 자동 브리핑 발송
