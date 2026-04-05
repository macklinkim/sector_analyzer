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
| 배포 | Vercel (프론트) + Railway/Render (백엔드) |
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
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx       # 루트 레이아웃 (Dark Mode)
│   │   │   ├── page.tsx         # 대시보드 메인
│   │   │   └── globals.css
│   │   ├── components/
│   │   │   ├── header/GlobalHeader.tsx
│   │   │   ├── sector/SectorHeatmap.tsx
│   │   │   ├── sector/SectorTrend.tsx
│   │   │   ├── news/NewsRadar.tsx
│   │   │   ├── news/ImpactCard.tsx
│   │   │   ├── rotation/RotationSignals.tsx
│   │   │   ├── chart/DeepDiveChart.tsx
│   │   │   └── ui/Skeleton.tsx
│   │   ├── lib/
│   │   │   ├── api.ts
│   │   │   └── utils.ts
│   │   └── types/index.ts
│   ├── next.config.ts
│   ├── tailwind.config.ts
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

```
┌──────────────────────────────────────────────────┐
│  Global Header                                    │
│  [S&P500 +0.5%] [NASDAQ +0.8%] [DOW +0.3%]      │
│  현재 국면: Goldilocks (60%)  갱신: 08:30 ET      │
├────────────────────┬─────────────────────────────┤
│  Sector Heatmap    │  News Impact Radar           │
│  & Rotation Signal │  [정치|경제|사회|글로벌] 탭    │
│                    │                              │
│  Treemap +         │  뉴스 목록 + Impact Card     │
│  유입/유출 화살표   │  (점수, 방향, 근거)           │
│  AI 요약 텍스트    │                              │
├────────────────────┴─────────────────────────────┤
│  Sector Scoreboard                                │
│  [섹터별 Final Score 바 차트 + Overweight/Under]   │
├──────────────────────────────────────────────────┤
│  Deep Dive Chart                                  │
│  인터랙티브 가격 차트 + 뉴스 마커 + 국면 배경색     │
└──────────────────────────────────────────────────┘
```

---

## 6. 디자인 가이드

- **테마:** Dark Mode 기본
- **색상:** 상승 `#22c55e`, 하락 `#ef4444`, 배경 `#0f172a`
- **국면 색상:** Goldilocks `#22c55e`, Reflation `#f59e0b`, Stagflation `#ef4444`, Deflation `#3b82f6`
- **UI:** 카드 레이아웃, 스켈레톤 로딩, 반응형
- **차트:** Recharts (Treemap, BarChart, AreaChart)

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
- Next.js + shadcn/ui 대시보드 구현
- 차트, 히트맵, 뉴스 피드, 스코어보드 컴포넌트

### Phase 5: 통합 + 배포
- E2E 통합 테스트
- Vercel + Railway 배포
- 면책 조항, 모니터링

### Phase 6 (후순위): Google 연동
- Google Sheets 누적 저장
- Gmail 자동 브리핑 발송
