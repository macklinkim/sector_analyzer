# AGENTS.md - AI Agent Architecture

## Overview

본 프로젝트는 LangGraph 기반 3개 에이전트 파이프라인으로 구성됩니다.
각 에이전트는 LangGraph 그래프의 노드(Node)로 동작하며, 공유 상태(State)를 통해 데이터를 전달합니다.

---

## Agent Pipeline

```
[Scheduler Trigger: 08:30 ET / 17:00 ET]
        │
        ▼
  ┌─────────────┐
  │  Data Agent  │  EODHD API → 섹터/지수/경제지표 수집
  └──────┬──────┘  Playwright MCP → 동적 금융 포털 스크래핑 (Heavy Track)
                   Claude Vision → 차트/히트맵 스크린샷 분석
         │ MarketAnalysisState.market_data
         ▼
  ┌─────────────┐
  │  News Agent  │  NewsAPI MCP + Fetch MCP → 뉴스 수집/원문 분석
  └──────┬──────┘  (Fallback: Google News RSS)
         │ MarketAnalysisState.news_data
         ▼
  ┌──────────────┐
  │ Analyst Agent │  Claude API → 4단계 판단 프로세스
  └──────┬───────┘
         │ MarketAnalysisState.analysis_results
         ▼
    [Supabase 저장]
```

---

## 1. Data Agent

**역할:** EODHD API를 통해 미국 주식 시장 데이터를 수집하고 정제

**입력:** 스케줄러 트리거 (batch_type: pre_market | post_market)

**출력:**
- 주요 지수 데이터 (S&P500, NASDAQ, DOW)
- 12개 섹터 ETF 데이터 (가격, 변동률, 거래량)
- 모멘텀 지표 계산 (1주, 1개월, 3개월, 6개월)
- 상대강도(RS) 계산 (섹터 수익률 / S&P500 수익률)
- 거래량 변화율 (현재 vs 20일 평균)
- 핵심 경제 지표 (금리, PMI, CPI 등)

**도구:**
- EODHD API 클라이언트 (`services/eodhd.py`) — Fast Track
- Playwright MCP — Heavy Track (동적 금융 포털 SPA 데이터 수집)
- Claude Vision — Playwright 스크린샷 기반 차트/히트맵 시각 분석

### 도구 이원화 전략 (Fast Track / Heavy Track)

```
┌─ Fast Track (EODHD API) ─────────────────────────┐
│  용도: 정형 데이터 (가격, 거래량, 지표)            │
│  지연: ~1초                                       │
│  호출: 매 배치마다                                 │
└──────────────────────────────────────────────────┘

┌─ Heavy Track (Playwright MCP) ───────────────────┐
│  용도: 동적 웹페이지의 비정형 ���이터              │
│        (SPA 렌더링 후 데이터, 인터랙티브 차트)     │
│  지연: 수 초 ~ 수십 초                             │
│  호출: 선택적 (API 미제공 데이터만)                │
│  + Claude Vision: 스크린샷 → 차트/히트맵 분석      │
└──────────────────────────────────────────────────┘
```

**원칙:** API로 얻을 수 있는 데이터는 반드시 Fast Track 사용. Playwright는 API가 제공하지 않는 동적 콘텐츠에만 사용.

**에러 처리:**
- API 호출 실패 → 최근 캐싱 데이터 사용 + 경고 로그
- Rate limit → 지수 백오프(exponential backoff)
- Playwright 차단(Anti-bot) → 해당 태스크 건너뛰기 + 경고 로그, API 데이터만으로 분석 진행

---

## 2. News Agent

**역할:** 4개 카테고리에서 주요 미국 뉴스를 수집하고 원문을 분석

**입력:** MarketAnalysisState.market_data (시장 맥락 참조)

**출력:**
- 카테고리별 주요 뉴스 3건 (정치, 경제, 사회, 글로벌 = 총 12건)
- 각 뉴스의 원문 요약 (Fetch MCP로 가져온 마크다운 기반)
- 뉴스 메타데이터 (제목, 출처, URL, 게시일)

**도구:**
- NewsAPI MCP 서버 (`mcp/news_server.py`) — 카테고리별 top-headlines 조회
- Fetch MCP (Anthropic 공식) — 뉴스 원문 웹페이지 → 마크다운 변환

**Fallback 전략:**
```
NewsAPI 호출 시도
    │
    ├─ 성공 → 뉴스 데이터 반환
    │
    └─ 실패 (429 Rate Limit / 500 Error)
        │
        ▼
    Google News RSS (feedparser)
        │
        ├─ 성공 → RSS 뉴스 데이터 반환
        └─ 실패 → 빈 뉴스 + 경고 로그, Analyst Agent에 "뉴스 없음" 상태 전달
```

**NewsAPI 호출 예산:**
- 1회 배치: 4회 호출 (카테고리 x 1)
- 1일 2회 배치: 8회/일
- 무료 한도 100회/일 대비 8% 사용

---

## 3. Analyst Agent

**역할:** 수집된 시장 데이터와 뉴스를 융합하여 섹터 로테이션 분석 수행

**입력:** MarketAnalysisState (market_data + news_data)

**AI 모델:** Claude API (Anthropic SDK)

**참조 데이터:**
- `docs/sector-rotation-strategy.md` — 시스템 프롬프트에 포함
- `sector_regime_mapping` 테이블 — RAG 참조

### 4단계 판단 프로세스

#### Step 1: Macro Regime Detection (매크로 국면 감지)
- 경제 지표 + 거시 뉴스 분석
- 4개 국면(Goldilocks/Reflation/Stagflation/Deflation) 확률 산출
- 국면 전환 가능성 판단

#### Step 2: Base Score Calculation (기본 점수 할당)
- sector_regime_mapping의 유리/불리 국면 기반
- 12개 섹터에 기본 모멘텀 점수 부여
- 전환 확률에 따른 가중 반영

#### Step 3: Override Adjustment (가중치 보정)
- 개별 뉴스의 섹터별 예외 규칙 검사
- override_rules 트리거 조건 매칭
- 점수 보정값 산출

#### Step 4: Scoring & Reporting (최종 리포팅)
- sector_scoreboards 생성 (섹터별 종합 점수 + 순위)
- rotation_signals 생성 (자금 이동 방향)
- market_reports 생성 (종합 시장 브리핑)
- Top 3 Overweight / Bottom 3 Underweight 선정

**출력:**
- `macro_regimes` 레코드
- `sector_scoreboards` 레코드 (12개 섹터)
- `rotation_signals` 레코드 (감지된 신호들)
- `news_impact_analyses` 레코드 (뉴스별 섹터 영향)
- `market_reports` 레코드 (종합 리포트)

---

## Shared State Schema

```python
class MarketAnalysisState(TypedDict):
    # 메타
    batch_type: str               # "pre_market" | "post_market"
    triggered_at: str             # ISO timestamp

    # Data Agent 출력
    market_data: MarketData       # 지수, 섹터, 경제지표

    # News Agent 출력
    news_data: NewsData           # 카테고리별 뉴스 + 원문 요약
    news_fallback_used: bool      # RSS fallback 사용 여부

    # Analyst Agent 출력
    analysis_results: AnalysisResults  # 국면, 점수, 신호, 리포트
```

---

## MCP Servers

### NewsAPI MCP Server (`mcp/news_server.py`)

커스텀 MCP 서버로 NewsAPI.org를 래핑하여 News Agent의 도구로 제공.

**도구 목록:**
- `get_top_headlines(category, country, page_size)` — 카테고리별 헤드라인 조회
- `search_news(query, from_date, to_date)` — 키워드 검색

### Fetch MCP (Anthropic 공식)

뉴스 원문 URL을 마크다운으로 변환하여 AI가 깊이 있게 분석할 수 있도록 지원.

### Playwright MCP (심화 스크래핑)

API가 제공되지 않는 대형 금융 포털의 동적 웹페이지(SPA) 데이터를 수집. 에이전트가 직접 클릭, 스크롤, 조건 설정(날짜 등)을 수행하며 브라우저 렌더링 후의 데이터를 마크다운으로 추출.

**도구 목록:**
- `navigate(url)` — 페이지 이동
- `click(selector)` — 요소 클릭 (탭 전환, 필터 설정 등)
- `screenshot(selector?)` — 전체 페이지 또는 특정 영역 캡처 → Claude Vision 분석 연동
- `extract_text(selector)` — 렌��링된 DOM에서 텍스트 추출
- `scroll(direction)` — 스크롤 (무한 스크롤 페이지 대응)

**사용 시나리오:**
- 금융 포털의 섹터 히트맵 캡처 → Vision으로 현재 시장 상태 벤치마킹
- 인터랙티브 차트에서 특정 기간 데이터 추출
- 실시간 뉴스 피드(SPA)에서 동적 로딩된 콘텐츠 수집

**제약사항:**
- Heavy Track 전용: 매 배치에서 선택적으로만 사용
- Anti-bot 차단 위험: Stealth 플러그인 또는 프록시 라우팅 필요 가능
- 리소스 집약적: 동시 실행 브라우저 인스턴스 수 제한 필요

---

## Error Handling & Resilience

| 장애 상황 | 대응 전략 |
| :--- | :--- |
| EODHD API 다운 | 최근 캐싱 데이터 사용, 경고 표시 |
| NewsAPI 한도 초과 | Google News RSS fallback 자동 전환 |
| Claude API 오류 | 재시도 (3회) + 실패 시 이전 분석 결과 유지 |
| Supabase 연결 실패 | 로컬 파일 임시 저장 + 복구 시 동기화 |
| 스케줄러 미스 | 다음 배치에서 누락 감지 후 보정 실행 |
| Playwright 봇 차단 | 해당 태스크 건너뛰기 + API 데이터만으로 분석 진행 |
| Playwright 타임아웃 | 30초 제한, 초과 시 스킵 + 경고 로그 |
