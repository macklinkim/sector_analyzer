# AI-Driven Market Insights Dashboard

> **미국 주식 시장의 섹터 순환매(Sector Rotation) 흐름을 AI로 분석하고 투자 인사이트를 제공하는 종합 대시보드**

Yahoo Finance + NewsAPI + Google News RSS --> LangGraph AI 3-Agent Pipeline --> Claude AI 분석 --> FastAPI + React SPA 대시보드

**Live Demo:** https://sectoranalyzerfrontend2026.kopserf.workers.dev (프론트엔드, Cloudflare Workers)

**Backend API:** https://sector-analyzer.onrender.com (FastAPI, Render)

---

## Table of Contents

- [Overview](#overview)
- [Screenshots](#screenshots)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [AI Pipeline (LangGraph)](#ai-pipeline-langgraph)
- [3-Step Signal Validation](#3-step-signal-validation)
- [Macro Regime Matrix](#macro-regime-matrix)
- [Dashboard Layout](#dashboard-layout)
- [Frontend Components](#frontend-components)
- [Backend API Endpoints](#backend-api-endpoints)
- [Data Services](#data-services)
- [Database Schema (Supabase)](#database-schema-supabase)
- [Scheduler & Batch Processing](#scheduler--batch-processing)
- [MCP Servers](#mcp-servers)
- [Claude Code Integration](#claude-code-integration)
- [Dependencies](#dependencies)
- [Quick Start](#quick-start)
- [Deployment](#deployment)
- [Environment Variables](#environment-variables)
- [Sector ETF List](#sector-etf-list)
- [Charts & Visualizations](#charts--visualizations)
- [Caching Strategy](#caching-strategy)
- [Development](#development)
- [Disclaimer](#disclaimer)

---

## Overview

이 프로젝트는 **거시 경제 국면(Macro Regime)** 변화를 실시간으로 감지하고, 11개 미국 섹터 ETF의 **로테이션 시그널**을 AI가 생성하는 투자 분석 대시보드입니다.

### 핵심 기능

| 기능 | 설명 |
|------|------|
| **Macro Regime Detection** | 거시 경제 국면(Goldilocks/Reflation/Stagflation/Deflation) AI 자동 판정 |
| **3-Step Signal Validation** | 매크로 환경 -> RS/모멘텀 교차 -> Claude AI 최종 검증 |
| **Sector Heatmap** | 11개 섹터 ETF Treemap + 구성종목 Sub-Treemap |
| **News Impact Feed** | 뉴스별 AI 한글 요약 + 섹터 임팩트 점수(0~10) + 카테고리 필터 |
| **Global Crises** | Google News RSS -> Claude AI 시장 파급력 위기 선별 |
| **AI Sector Screener** | 국면 기반 섹터 점수 + 추천(Overweight/Neutral/Underweight) |
| **Economic Calendar** | US10Y, DXY, WTI, Gold 실시간 거시 지표 |
| **Rotation Signals** | MAJOR/ALERT/WATCH 3등급 시그널 + 확신도(Confidence Score) |
| **자동 배치** | 매일 2회(Pre-Market 08:30 ET, Post-Market 17:00 ET) 자동 분석 |
| **한글 UI** | 섹터/지수/카테고리 한글 라벨 (i18n) |
| **로그인** | 허가제 이름 기반 접근 제어 |

---

## Architecture

### High-Level Architecture

```
+------------------+     +------------------+     +------------------+
|   Yahoo Finance  |     |    NewsAPI.org    |     |  Google News RSS |
|  (Market Data)   |     |  (News Articles) |     | (Global Crises)  |
+--------+---------+     +--------+---------+     +--------+---------+
         |                         |                         |
         v                         v                         v
+--------+---------+     +--------+---------+     +--------+---------+
|   Data Agent     |     |   News Agent     |     |  Crises Pipeline |
|  (LangGraph)     |     |  (LangGraph)     |     |  (Claude AI)     |
+--------+---------+     +--------+---------+     +--------+---------+
         |                         |                         |
         +------------+------------+                         |
                      |                                      |
              +-------v--------+                             |
              | Analyst Agent  |                             |
              | (Claude API)   |                             |
              | 3-Step Valid.  |                             |
              +-------+--------+                             |
                      |                                      |
              +-------v--------+                             |
              |   Supabase     |<----------------------------+
              |  (PostgreSQL)  |
              +-------+--------+
                      |
              +-------v--------+
              |   FastAPI      |
              |  REST API      |
              +-------+--------+
                      |
              +-------v--------+
              |  React SPA     |
              | (Vite + TS)    |
              +----------------+
```

### Request Flow

```
Browser -> FastAPI Static (SPA) -> React App
React App -> /api/* -> FastAPI Routes -> Supabase -> Response
Scheduler -> LangGraph Pipeline -> Data/News/Analyst Agents -> Supabase
```

---

## Tech Stack

### Backend

| 기술 | 버전 | 용도 |
|------|------|------|
| **Python** | 3.12+ | Runtime |
| **FastAPI** | >= 0.115.0 | REST API 프레임워크 |
| **uvicorn** | >= 0.30.0 | ASGI 서버 (Standard extras: watchfiles, uvloop, httptools) |
| **LangGraph** | >= 0.4.0 | AI Agent 오케스트레이션 (StateGraph 기반) |
| **LangChain** | >= 0.3.0 | LLM 통합 프레임워크 |
| **LangChain-Anthropic** | >= 0.3.0 | Claude API 연동 |
| **Anthropic SDK** | >= 0.40.0 | Claude API 직접 호출 (Sonnet 4) |
| **yfinance** | >= 0.2.40 | Yahoo Finance 데이터 수집 (무료) |
| **Pydantic** | >= 2.0.0 | 데이터 검증 & 직렬화 (v2) |
| **Pydantic-Settings** | >= 2.0.0 | 환경변수 관리 |
| **Supabase Python** | >= 2.0.0, < 2.10.0 | PostgreSQL 클라이언트 |
| **APScheduler** | >= 3.10.0, < 4.0.0 | 크론 기반 배치 스케줄러 |
| **httpx** | >= 0.27.0 | 비동기 HTTP 클라이언트 |
| **feedparser** | >= 6.0.0 | RSS 피드 파싱 (Google News) |
| **aiofiles** | >= 24.0.0 | 비동기 파일 I/O |
| **tzdata** | >= 2024.1 | 타임존 데이터 (Docker slim 이미지용) |
| **python-dotenv** | >= 1.0.0 | .env 파일 로드 |

### Frontend

| 기술 | 버전 | 용도 |
|------|------|------|
| **React** | 19.2+ | UI 라이브러리 |
| **Vite** | 8.0+ | 빌드 도구 & 개발 서버 |
| **TypeScript** | 5.9+ | 정적 타입 (strict mode) |
| **Tailwind CSS** | 4.2+ | 유틸리티 기반 스타일링 (v4, CSS-first) |
| **Recharts** | 3.8+ | 차트 라이브러리 (Treemap, BarChart, AreaChart) |
| **shadcn/ui** | - | Card, Badge, Skeleton 등 UI 컴포넌트 |
| **class-variance-authority** | 0.7+ | 조건부 CSS 클래스 (Badge variants) |
| **clsx + tailwind-merge** | - | Tailwind 클래스 병합 유틸리티 |
| **Lucide React** | 1.7+ | 아이콘 라이브러리 |

### Infrastructure

| 기술 | 용도 |
|------|------|
| **Docker** | 멀티 스테이지 빌드 (Node 22 + Python 3.12-slim) |
| **Render** | 클라우드 배포 (무료 티어, Docker 기반) |
| **Supabase** | PostgreSQL + Auth + Realtime (클라우드 DB) |
| **Git / GitHub** | 버전 관리 + Render Auto-Deploy |

### AI & Data

| 기술 | 용도 |
|------|------|
| **Claude Sonnet 4** | 국면 분석, 섹터 스코어링, 뉴스 요약, 위기 필터링 |
| **LangGraph StateGraph** | 3-Agent 순차 파이프라인 오케스트레이션 |
| **Yahoo Finance (yfinance)** | 주가, 섹터 ETF, 거시 지표, 히스토리 데이터 |
| **NewsAPI.org** | 뉴스 기사 수집 (business, technology, science, general) |
| **Google News RSS** | 글로벌 위기 헤드라인 수집 (fallback) |

### Dev Tools

| 기술 | 용도 |
|------|------|
| **Claude Code** | AI 페어 프로그래밍 (Opus 4.6, 1M context) |
| **Superpowers Plugin** | 브레인스토밍, TDD, 코드 리뷰 스킬 |
| **Playwright MCP** | 배포 사이트 자동 점검 & 스크린샷 |
| **pytest** | 백엔드 테스트 (pytest-asyncio, pytest-cov) |
| **Ruff** | Python 린터 (target: py312, line-length: 100) |
| **ESLint** | TypeScript/React 린터 |

---

## Project Structure

```
economi_analyzer/
├── .claude/                        # Claude Code 설정
│   ├── rules/
│   │   ├── agent-prompts.md        # AI Agent 프롬프트 규칙
│   │   ├── backend.md              # Python/FastAPI 코딩 컨벤션
│   │   └── frontend.md             # TypeScript/React 디자인 시스템
│   ├── settings.json               # 권한 설정 & 훅
│   └── settings.local.json         # 로컬 오버라이드
│
├── backend/                        # FastAPI + LangGraph 파이프라인
│   ├── app/
│   │   ├── agents/                 # LangGraph 에이전트 노드
│   │   │   ├── graph.py            # StateGraph 빌드 (Data->News->Analyst)
│   │   │   ├── state.py            # MarketData, NewsData, AnalysisResults 타입
│   │   │   ├── data_agent.py       # Yahoo Finance 데이터 수집
│   │   │   ├── news_agent.py       # NewsAPI + RSS fallback 뉴스 수집
│   │   │   └── analyst_agent.py    # 3-Step Validation AI 분석
│   │   ├── api/
│   │   │   ├── routes/
│   │   │   │   ├── analysis.py     # /api/analysis/* (trigger, report, signals)
│   │   │   │   ├── market.py       # /api/market/* (indices, sectors, indicators)
│   │   │   │   ├── news.py         # /api/news/* (articles, summaries, crises)
│   │   │   │   ├── auth.py         # /api/auth/* (login, verify)
│   │   │   │   └── health.py       # /health
│   │   │   └── deps.py             # FastAPI 의존성 주입
│   │   ├── models/                 # Pydantic v2 스키마
│   │   │   ├── analysis.py         # MacroRegime, SectorScoreboard, RotationSignal
│   │   │   ├── market.py           # MarketIndex, Sector, EconomicIndicator
│   │   │   └── news.py             # NewsArticle, NewsImpactAnalysis
│   │   ├── services/               # 외부 API 클라이언트
│   │   │   ├── yahoo_finance.py    # YahooFinanceService (yfinance 래퍼)
│   │   │   ├── eodhd.py            # EODHDService (레거시, 유료 전환됨)
│   │   │   ├── newsapi.py          # NewsAPI.org 클라이언트
│   │   │   ├── reliefweb.py        # Google News RSS + Claude AI 위기 필터
│   │   │   ├── rss_fallback.py     # RSS 뉴스 fallback
│   │   │   ├── sector_stocks.py    # 섹터별 구성종목 딕셔너리
│   │   │   └── supabase.py         # Supabase CRUD + dedup 로직
│   │   ├── scheduler/
│   │   │   └── jobs.py             # APScheduler 크론잡 (08:30, 17:00 ET)
│   │   ├── mcp/
│   │   │   └── news_server.py      # NewsAPI MCP 서버
│   │   ├── config.py               # pydantic-settings 환경변수
│   │   └── main.py                 # FastAPI 앱 + CORS + 스케줄러 + SPA 서빙
│   ├── supabase/migrations/        # DB 마이그레이션 SQL
│   │   ├── 001_initial_schema.sql  # 7개 테이블 생성
│   │   ├── 002_add_momentum_1y.sql # momentum_1y 컬럼
│   │   └── 003_add_week_52_range.sql # week_52_low/high 컬럼
│   ├── tests/                      # pytest 테스트
│   └── pyproject.toml              # Python 의존성 + 도구 설정
│
├── frontend/                       # Vite + React SPA
│   ├── src/
│   │   ├── components/
│   │   │   ├── auth/               # LoginGate (허가제 로그인)
│   │   │   ├── header/             # GlobalMacroHeader, TickerBar, RegimeBadge
│   │   │   ├── sector/             # SectorHeatmap, SectorStockTreemap, Sparkline, Movers
│   │   │   ├── news/               # NewsImpactFeed, ImpactCard, EconomicCalendar
│   │   │   ├── chart/              # MultiChartGrid, MomentumBar, RelativeStrength, RangeChart, EventMarker
│   │   │   ├── screener/           # AiScreenerTable
│   │   │   └── ui/                 # Skeleton, Badge, Card (shadcn/ui 기반)
│   │   ├── hooks/                  # React 커스텀 훅
│   │   │   ├── useMarketData.ts    # 지수/섹터/지표/국면 데이터
│   │   │   ├── useNewsData.ts      # 뉴스/임팩트/위기 데이터
│   │   │   └── useAnalysisData.ts  # 스코어보드/시그널/리포트
│   │   ├── lib/
│   │   │   ├── api.ts              # fetch wrapper + 엔드포인트 정의
│   │   │   ├── utils.ts            # formatPrice, formatPercent, cn()
│   │   │   └── i18n.ts             # 섹터/카테고리 한글 라벨
│   │   ├── types/index.ts          # TypeScript 인터페이스 전체
│   │   ├── App.tsx                 # 루트 컴포넌트 (4-Area 레이아웃)
│   │   ├── main.tsx                # React 진입점
│   │   └── index.css               # Tailwind CSS + 테마 변수
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts
│
├── docs/
│   ├── sector-rotation-strategy.md # 섹터 로테이션 전략 매트릭스
│   ├── installation-guide.md       # 설치 가이드
│   └── superpowers/
│       ├── plans/                  # 5-Phase 개발 계획
│       └── specs/                  # 설계 스펙 문서
│
├── .mcp.json                       # MCP 서버 설정
├── Dockerfile                      # 멀티 스테이지 Docker 빌드
├── render.yaml                     # Render 배포 설정
├── CLAUDE.md                       # Claude Code 프로젝트 지침
└── AGENTS.md                       # AI Agent 프롬프트 가이드
```

---

## AI Pipeline (LangGraph)

### StateGraph Flow

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Data Agent    │───>│   News Agent    │───>│  Analyst Agent  │───> END
│                 │    │                 │    │                 │
│ Yahoo Finance   │    │ NewsAPI.org     │    │ Claude Sonnet 4 │
│ - 3 Indices     │    │ - 4 Categories  │    │ - Step 1: Macro │
│ - 11 Sector ETFs│    │ - 3 articles/cat│    │ - Step 2: RS/Mom│
│ - 4 Macro Indic.│    │ RSS fallback    │    │ - Step 3: Claude│
│ - Momentum      │    │                 │    │                 │
│ - RS            │    │                 │    │                 │
│ - 52W Range     │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Shared State (TypedDict)

```python
class MarketAnalysisState(TypedDict):
    batch_type: str                    # "pre_market" | "post_market" | "manual"
    triggered_at: str                  # ISO timestamp
    market_data: MarketData | None     # indices, sectors, indicators, momentum, RS
    news_data: NewsData | None         # articles_by_category
    news_fallback_used: bool           # RSS fallback 사용 여부
    analysis_results: AnalysisResults | None  # regime, scoreboards, signals, report
```

### Agent Details

#### Data Agent (`data_agent.py`)
- **입력:** batch_type
- **출력:** MarketData (indices, sectors, economic_indicators, momentum, relative_strength)
- **데이터 소스:** Yahoo Finance (`yfinance` 라이브러리)
  - `yf.download()` — 배치 다운로드 (섹터 ETF, 인덱스)
  - `yf.Ticker().history()` — 개별 심볼 (매크로 지표: ^TNX, CL=F 등)
- **계산:** 모멘텀(1W/1M/3M/6M/1Y), 상대강도(vs SPY), 52주 범위

#### News Agent (`news_agent.py`)
- **입력:** MarketData
- **출력:** NewsData (articles_by_category)
- **소스:** NewsAPI.org (politics, business, society, world) -> RSS fallback
- **한도 관리:** 100 req/day, 카테고리별 top 3

#### Analyst Agent (`analyst_agent.py`)
- **입력:** MarketData + NewsData
- **출력:** AnalysisResults (regime, scoreboards, rotation_signals, report)
- **모델:** Claude Sonnet 4 (`claude-sonnet-4-20250514`)
- **로직:** 3-Step Validation (아래 참조)

---

## 3-Step Signal Validation

기존 문제점: 모든 섹터에 `Regime Shift` 시그널이 동시 10건 발생 (Fake Signals)

### Step 1: Macro Environment Check (규칙 기반)

경제 지표의 **방향성 조합**으로 시장 환경을 분류합니다.

| 지표 | 상승(up) | 하락(down) |
|------|----------|-----------|
| **US 10Y** | inflation_score +1, risk_on -0.5 | inflation_score -1, risk_on +0.5 |
| **DXY** | risk_on -0.5 | risk_on +1 |
| **WTI** | inflation_score +1 | inflation_score -1 |
| **Gold** | risk_on -1, inflation -1 | risk_on +1 |

**결과 분류:**

| risk_on | inflation | 환경 | 유리 섹터 |
|---------|-----------|------|----------|
| > 0 | <= 0 | **Risk-On** | XLK, XLY, XLC, XLF |
| > 0 | > 0 | **Inflationary** | XLE, XLB, XLI |
| <= 0 | <= 0 | **Deflationary** | XLU, XLV, XLP, XLRE |
| <= 0 | > 0 | **Risk-Off** | XLU, XLV, XLP, XLE |

### Step 2: RS & Momentum Pre-filter (규칙 기반)

| 조건 | 점수 | 설명 |
|------|------|------|
| RS > 2.0% | +0.3 | 상대강도 강세 |
| RS 골든크로스 (RS>0 & 1M<0) | +0.2 | 약세에서 전환 중 |
| 1W/1M/3M 모두 양수 | +0.2 | 모멘텀 정렬 |
| 1W > 1M (단기 회복) | +0.15 | 단기 회복세 |
| 매크로 환경 일치 | +0.1~0.3 | 환경별 가점 |
| 매크로 불일치 & RS 강세 | -0.15 | Fake Signal 패널티 |

**score < 0.2인 후보는 제외**

### Step 3: Claude AI Final Analysis

사전 필터된 후보만 Claude에게 전달하여 최종 검증:

| 시그널 등급 | 조건 | 확신도 | 빈도 |
|------------|------|--------|------|
| **MAJOR** (강력 전환) | 매크로 변화 + RS 골든크로스 + 거래량 동반 | >= 70% | 월 1~2회/섹터 |
| **ALERT** (수급 포착) | 뉴스 촉매 + 1W 모멘텀 급증 + RS 양수 | 50~70% | 주 1~2회 |
| **WATCH** (개선 중) | RS 마이너스->플러스 전환, 방어적 관점 | 30~50% | 상시 |

**제한:** 최대 5개 시그널/실행, 확신도 30% 미만 자동 제거

---

## Macro Regime Matrix

2D 매크로 국면 매트릭스 (성장 x 물가):

```
                    Inflation HIGH
                         |
         Reflation       |       Stagflation
         (성장+물가)       |       (침체+물가)
         XLE, XLB, XLI   |       XLE, XLV, XLP
                         |
   ─────────────────────+──────────────────── Growth
                         |
         Goldilocks      |       Deflation
         (성장+저물가)     |       (침체+저물가)
         XLK, XLY, XLC   |       XLU, XLV, XLRE
                         |
                    Inflation LOW
```

### Override Rules (특수 조건)

| 조건 | 효과 |
|------|------|
| 금리 인하 뉴스 + Deflation | XLRE(부동산) 강력 매수 신호 |
| 지정학적 리스크 + Stagflation | XLE(에너지) 방어주 업그레이드 |
| 실질금리 하락 + Deflation | XLK(기술) 방어적 자산으로 재분류 |
| 고용 악화 뉴스 | XLY(경기소비재) 하향 조정 |

---

## Dashboard Layout

2026-04-11 리팩토링으로 **Sticky 헤더 + 2탭 구조**로 전환되었습니다. `GlobalMacroHeader`와 `DashboardTabs`가 스크롤과 무관하게 상단에 고정되며, 탭 선택은 `localStorage`에 영속됩니다.

```
+==================================================================+
|  [STICKY] Global Macro Header  (z-40, 스크롤해도 고정)            |
|  나스닥 21,879 +0.18% | 다우 46,504 -0.13% | S&P500 6,582 +0.11% |
|  WTI $110.14 | US10Y 4.31 | DXY 99.94 | Gold $4,705               |
|  현재 국면: Reflation (60%)                                        |
|------------------------------------------------------------------|
|  [ 시장 현황 ]  [ AI 인사이트 ]   <- DashboardTabs (sticky)        |
+==================================================================+

        ▼ 시장 현황 탭 (MarketTab — Yahoo Finance raw data)
+------------------------------------------------------------------+
|  Row 1: SectorHeatmap (풀폭, Treemap 섹터 진입점)                  |
+------------------------------------------------------------------+
|  Row 2: SectorStockTreemap (풀폭, 선택 섹터 구성종목)              |
+---------------------------------+--------------------------------+
|  Row 3: SectorSparkline         |  NewsImpactFeed                |
|         30일 AreaChart          |  전체/경제/정치/사회/글로벌 탭 |
+---------------------------------+--------------------------------+
|  Row 4: MarketMovers            |  EconomicCalendar              |
|         Gainers/Losers/Volume   |  US10Y, DXY, WTI, Gold         |
+------------------------------------------------------------------+
|  Row 5: RelativeStrength (풀폭, BarChart RS vs SPY)                |
+------------------------------------------------------------------+
|  Row 6: MomentumBar (풀폭, 1W/1M/3M/1Y Grouped BarChart)           |
+------------------------------------------------------------------+
|  Row 7: RangeChart (풀폭, 52주 Bullet Chart)                       |
+------------------------------------------------------------------+

        ▼ AI 인사이트 탭 (AiTab — AI 파이프라인 판단)
+---------------------------------+--------------------------------+
|  Row 1a: BusinessCycleClock     |  Row 1b: RelativeRotationGraph |
|          4국면 원형 시계         |          RS-Ratio x Momentum  |
|          (360x360 확대)          |          Scatter + 4사분면    |
+---------------------------------+--------------------------------+
|  Row 2: AiRotationSignals (풀폭)                                  |
|   [MAJOR 🔴] XLU +0.72  confidence 72%  · reasoning 좌측 정렬      |
|   [ALERT 🟡] XLE +0.58  confidence 58%  · reasoning 좌측 정렬      |
|   ... (각 카드 reasoning 항상 표시, 날짜 바로 왼쪽)                |
+------------------------------------------------------------------+
|  Row 3: AiScreenerTable (풀폭)                                    |
|  Rank | Sector | ETF | AI Score | Base | News | Mom | Signal     |
+------------------------------------------------------------------+
```

### 탭 설계 원칙

| 탭 | 역할 | 컴포넌트 |
|---|---|---|
| **시장 현황** | Yahoo Finance raw data 레이어 (외부 API 원본) | SectorHeatmap, SectorStockTreemap, SectorSparkline, MarketMovers, NewsImpactFeed, EconomicCalendar, SectorComparisonCharts(RelativeStrength/MomentumBar/RangeChart) |
| **AI 인사이트** | AI 파이프라인 판단 레이어 (추론/시그널) | BusinessCycleClock, RelativeRotationGraph, AiRotationSignals, AiScreenerTable |

- **`selectedSector`는 두 탭이 공유** — Tab 2에서 섹터 클릭 후 Tab 1로 돌아가도 동일 섹터가 유지
- **데이터 훅(`useMarketData`/`useNewsData`/`useAnalysisData`)은 `Dashboard` 최상위에서 1회 호출** — 탭 전환 시 재요청 없음 (단일 진실 원천)
- **비활성 탭은 언마운트** — 차트 DOM/리스너 비용 절감 (Recharts 재마운트 시 스케일 재계산 비용은 허용)
- **`useStickyState` lazy initializer로 first-paint flash 방지** — localStorage에 저장된 탭이 첫 렌더에 즉시 적용

---

## Frontend Components

### Sticky Header

| 컴포넌트 | 파일 | 기능 |
|---------|------|------|
| `GlobalMacroHeader` | `header/GlobalMacroHeader.tsx` | 지수 + 거시 지표 + 국면 배지 전체 래퍼 |
| `TickerBar` | `header/TickerBar.tsx` | 지수 + 거시 지표 티커 (이름 매핑, 화살표) |
| `RegimeBadge` | `header/RegimeBadge.tsx` | 현재 국면 배지 (Goldilocks/Reflation/...) |

### Layout (2탭 구조, 2026-04-11 도입)

| 컴포넌트 | 파일 | 기능 |
|---------|------|------|
| `DashboardTabs` | `layout/DashboardTabs.tsx` | WAI-ARIA tablist, 2개 탭 ("시장 현황" / "AI 인사이트"), Tab+Space/Enter 키보드 전환 |
| `MarketTab` | `layout/MarketTab.tsx` | Tab 1 "시장 현황" 7-Row 패널 (Heatmap → StockTreemap 풀폭 → Sparkline+News → Movers+Calendar → RS → Momentum → Range) |
| `AiTab` | `layout/AiTab.tsx` | Tab 2 "AI 인사이트" 3-Row 패널 (BCC+RRG 2열 → AiRotationSignals → AiScreenerTable) |

### Sector (Market Tab)

| 컴포넌트 | 파일 | 기능 |
|---------|------|------|
| `SectorHeatmap` | `sector/SectorHeatmap.tsx` | Recharts Treemap, volume 기반 크기, 7단계 색상 |
| `SectorStockTreemap` | `sector/SectorStockTreemap.tsx` | 구성종목 Sub-Treemap (Top 15 + ETC), 풀폭 배치, localStorage 4시간 캐시 |
| `SectorSparkline` | `sector/SectorSparkline.tsx` | 30일 AreaChart + 그라데이션, 번들 API 1회 호출 |
| `MarketMovers` | `sector/MarketMovers.tsx` | Top Gainers/Losers/Volume, localStorage 4시간 캐시 |

### News (Market Tab)

| 컴포넌트 | 파일 | 기능 |
|---------|------|------|
| `NewsImpactFeed` | `news/NewsImpactFeed.tsx` | 탭 필터 (전체/경제/정치/사회/글로벌) + CrisisCard |
| `ImpactCard` | `news/ImpactCard.tsx` | 뉴스 카드: 제목, AI 한글 요약, 임팩트 점수, 섹터 |
| `EconomicCalendar` | `news/EconomicCalendar.tsx` | 거시 지표 4개: US10Y, DXY, WTI, Gold |

### Chart

| 컴포넌트 | 파일 | 사용 탭 | 기능 |
|---------|------|---------|------|
| `SectorComparisonCharts` | `chart/SectorComparisonCharts.tsx` | 시장 현황 | 3차트 세로 풀폭 스택 (RS → Momentum → Range). 구 `MultiChartGrid`를 리네임 + 단순화 |
| `RelativeStrength` | `chart/RelativeStrength.tsx` | 시장 현황 | BarChart (RS vs SPY), 양수 바 외부 상단 라벨 + 음수 바 내부 zero-line 라벨 (흰색) |
| `MomentumBar` | `chart/MomentumBar.tsx` | 시장 현황 | Grouped BarChart (1W/1M/3M/1Y), 커스텀 Legend |
| `RangeChart` | `chart/RangeChart.tsx` | 시장 현황 | 52주 Bullet Chart (11 섹터, 5열 그리드) |
| `BusinessCycleClock` | `chart/BusinessCycleClock.tsx` | AI 인사이트 | 360×360 확대된 4국면 원형 시계, Framer Motion 포인터. 기존 `header/` → `chart/` 이동 |
| `RelativeRotationGraph` | `chart/RelativeRotationGraph.tsx` | AI 인사이트 | Recharts ScatterChart, RS-Ratio × RS-Momentum, 4사분면 (Leading/Improving/Weakening/Lagging), 축 tick 소수점 2자리 |
| `AiRotationSignals` | `chart/AiRotationSignals.tsx` | AI 인사이트 | `EventMarker` 경량 래퍼, 향후 AI 시그널 전용 기능(필터/정렬) 확장 포인트 |
| `EventMarker` | `chart/EventMarker.tsx` | AI 인사이트 | MAJOR/ALERT/WATCH 등급, 확신도 바, reasoning 항상 표시 (날짜 좌측, `flex-1`) |

### Screener (AI Tab)

| 컴포넌트 | 파일 | 기능 |
|---------|------|------|
| `AiScreenerTable` | `screener/AiScreenerTable.tsx` | AI Score 기반 랭킹 테이블, Overweight/Neutral/Underweight, 섹터 행 클릭 시 `selectedSector` 동기화 |

### Hooks

| 훅 | 파일 | 기능 |
|---|------|------|
| `useMarketData` | `hooks/useMarketData.ts` | 지수/섹터/거시지표/국면 데이터 fetch + localStorage TTL 캐시 |
| `useNewsData` | `hooks/useNewsData.ts` | 뉴스 요약/임팩트/글로벌 위기 fetch + localStorage TTL 캐시 |
| `useAnalysisData` | `hooks/useAnalysisData.ts` | 스코어보드/시그널/리포트 fetch + localStorage TTL 캐시 |
| `useStickyState` | `hooks/useStickyState.ts` | 제네릭 localStorage 영속 상태 훅. **lazy initializer 패턴**으로 첫 페인트 flash 방지 (2026-04-11 도입) |
| `useAuth` | `components/auth/LoginGate.tsx` 내부 | 세션 토큰 관리 |

### Common UI

| 컴포넌트 | 기반 | 기능 |
|---------|------|------|
| `LoginGate` | Custom | 허가제 로그인 게이트 (ALLOWED_USERS 검증), 네트워크 에러 graceful handling |
| `LoadingScreen` | Custom | 로딩 모달 (반투명 배경 + 텍스트, `z-50`으로 sticky 헤더 `z-40` 위 오버레이) |
| `Card` | shadcn/ui | Card/CardHeader/CardContent/CardTitle |
| `Badge` | shadcn/ui + CVA | bullish/bearish/regime variants |
| `Skeleton` | shadcn/ui | 로딩 스켈레톤 |

---

## Backend API Endpoints

### Health

| Method | Path | 설명 |
|--------|------|------|
| GET | `/health` | 헬스체크 |

### Auth (`/api/auth`)

| Method | Path | 설명 |
|--------|------|------|
| POST | `/api/auth/login` | 로그인 (name 기반, ALLOWED_USERS 검증) |
| GET | `/api/auth/verify` | 세션 토큰 검증 |

### Market (`/api/market`)

| Method | Path | 설명 |
|--------|------|------|
| GET | `/api/market/indices` | 주요 지수 (S&P500, NASDAQ, DOW) |
| GET | `/api/market/sectors` | 11개 섹터 ETF (dedup 적용) |
| GET | `/api/market/indicators` | 경제 지표 (US10Y, DXY, WTI, Gold) |
| GET | `/api/market/regime` | 현재 매크로 국면 |
| GET | `/api/market/sector-history/{etf}?days=30` | 개별 섹터 히스토리 |
| GET | `/api/market/sectors-with-history?days=30` | 전체 섹터 + 스파크라인 번들 |
| GET | `/api/market/sector-stocks/{etf}` | 구성종목 Top 15 (4시간 캐시) |

### News (`/api/news`)

| Method | Path | 설명 |
|--------|------|------|
| GET | `/api/news/articles?category=&limit=` | 뉴스 목록 |
| GET | `/api/news/summaries?limit=` | Claude AI 한글 요약 포함 |
| GET | `/api/news/impacts` | 뉴스 임팩트 분석 |
| GET | `/api/news/crises` | 글로벌 위기 (Google News RSS + Claude AI, 1시간 캐시) |

### Analysis (`/api/analysis`)

| Method | Path | 설명 |
|--------|------|------|
| GET | `/api/analysis/report` | 최신 AI 분석 리포트 |
| GET | `/api/analysis/scoreboards` | 섹터 스코어보드 (12개) |
| GET | `/api/analysis/signals` | 로테이션 시그널 (최근 20건) |
| POST | `/api/analysis/trigger` | 수동 파이프라인 실행 (X-API-Key 필요) |

---

## Data Services

### YahooFinanceService (`yahoo_finance.py`)

EODHD API 유료 전환 이후 **무료 대안**으로 교체됨.

| 메서드 | 기능 | yfinance API |
|--------|------|-------------|
| `fetch_indices()` | S&P500, NASDAQ, DOW | `yf.download(["^GSPC","^IXIC","^DJI"])` |
| `fetch_sector_etfs()` | 11개 섹터 ETF 일괄 | `yf.download([11 symbols])` |
| `fetch_economic_indicators()` | US10Y, DXY, WTI, Gold | `yf.Ticker(sym).history()` (개별) |
| `calculate_momentum(sym)` | 1W/1M/3M/6M/1Y 수익률 | 1년 히스토리 기반 계산 |
| `calculate_52week_range(sym)` | 52주 고저 | 1년 히스토리 min/max |
| `calculate_relative_strength(sym)` | RS vs SPY | 섹터 1M - SPY 1M |
| `fetch_historical(sym, limit)` | 가격 히스토리 | 스파크라인/차트용 |
| `fetch_sector_stocks(symbols)` | 구성종목 일괄 | `yf.download(15 symbols)` |

**비동기 처리:** `ThreadPoolExecutor`(4 workers) + `asyncio.run_in_executor()`

### NewsAPI Service (`newsapi.py`)

| 기능 | 설명 |
|------|------|
| 4개 카테고리 수집 | politics, business, society, world |
| 일일 한도 관리 | 100 req/day (배치 캐싱) |
| RSS Fallback | NewsAPI 실패 시 `rss_fallback.py` 활성화 |

### Global Crises Pipeline (`reliefweb.py`)

```
Google News RSS (World) --> 20 Headlines --> Claude AI Filter --> 4~5 시장 파급력 위기
```

| 필드 | 설명 |
|------|------|
| title | 한글 제목 |
| summary | 1~2줄 한글 요약 |
| impact_score | 1~10 시장 영향도 |
| affected_sector | 영향 섹터명 |
| sentiment | negative/neutral/positive |

---

## Database Schema (Supabase)

### 테이블 목록

| 테이블 | 설명 | 주요 컬럼 |
|--------|------|----------|
| `market_indices` | 주요 지수 | symbol, name, price, change_percent |
| `sectors` | 섹터 ETF | name, etf_symbol, price, volume, momentum_*, RS, 52w |
| `economic_indicators` | 거시 지표 | indicator_name, value, previous_value, change_direction |
| `news_articles` | 뉴스 기사 | title, source, url (UNIQUE), category, summary |
| `news_impact_analyses` | 뉴스 임팩트 | news_url, impact_score, reasoning |
| `macro_regimes` | 매크로 국면 | regime, growth_direction, inflation_direction, probabilities |
| `sector_scoreboards` | 섹터 스코어 | sector_name, etf_symbol, final_score, rank, recommendation |
| `rotation_signals` | 로테이션 시그널 | signal_type, signal_grade, confidence_score, reasoning |
| `market_reports` | AI 리포트 | summary, key_highlights, disclaimer |
| `sector_regime_mapping` | 국면-섹터 매핑 | override_rules, display_order |

### Migrations

```sql
-- 001: 초기 스키마 (7개 테이블)
-- 002: sectors 테이블에 momentum_1y DECIMAL 추가
-- 003: sectors 테이블에 week_52_low, week_52_high DECIMAL 추가
```

---

## Scheduler & Batch Processing

### APScheduler Configuration

```python
scheduler = BackgroundScheduler(timezone="US/Eastern")

# Pre-Market: 08:30 AM ET (시장 개장 전)
scheduler.add_job(run_batch, CronTrigger(hour=8, minute=30), args=["pre_market"])

# Post-Market: 05:00 PM ET (시장 마감 후)
scheduler.add_job(run_batch, CronTrigger(hour=17, minute=0), args=["post_market"])
```

### Batch Flow

```
run_batch("pre_market")
  --> build_graph()                    # LangGraph StateGraph 빌드
  --> graph.ainvoke(initial_state)     # 3-Agent 파이프라인 실행
  --> _persist_results(result, svc)    # Supabase 저장
      --> indices, sectors, indicators, news, regime, scoreboards, signals, report
```

---

## MCP Servers

`.mcp.json` 설정:

| MCP 서버 | 패키지 | 용도 |
|---------|--------|------|
| **Fetch** | `@anthropic-ai/fetch-mcp` | HTTP 요청 (외부 API 호출) |
| **Playwright** | `@anthropic-ai/playwright-mcp` | 브라우저 자동화 (사이트 점검, 스크린샷) |
| **NewsAPI** | `app.mcp.news_server` (커스텀) | NewsAPI.org 래퍼 |
| **Supabase** | `@anthropic-ai/supabase-mcp` (플러그인) | DB 직접 접근 |
| **Chrome DevTools** | `@anthropic-ai/chrome-devtools-mcp` (플러그인) | DevTools 디버깅 |

---

## AI Packages — 프로젝트에서의 역할 상세

이 프로젝트는 9개의 AI 관련 패키지를 사용하며, 크게 **3개 계층**으로 나뉜다.

### Layer 1: Core AI Engine — `anthropic`

프로젝트의 **AI 두뇌**. Claude API를 직접 호출하여 자연어 분석 결과를 JSON 구조화 데이터로 변환한다.

```python
client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=4096,
    messages=[{"role": "user", "content": prompt}],
)
```

**4개 사용처와 각각의 기여:**

| 사용처 | 입력 | 출력 | 기여 |
|--------|------|------|------|
| **Analyst Agent (Step 3)** | 매크로 환경 + 모멘텀 + 뉴스 + RS | JSON: regime, scoreboards, signals | 11개 섹터 교차 분석을 ~10초에 수행 |
| **News Agent (AI Filter)** | 뉴스 기사 20~30건 | Noise/Context/Actionable 분류 | 뉴스 노이즈 90%+ 필터링 |
| **Global Crisis Pipeline** | Google News 위기 헤드라인 20건 | 시장 파급력 상위 4~5건 + 한글 요약 | UN/지정학 리스크의 시장 영향 평가 |
| **News Summarizer** | 영어 뉴스 기사 | 한글 1~2문장 요약 + 임팩트 점수 | 비영어권 사용자 접근성 향상 |

**왜 anthropic SDK를 직접 사용하는가?** LangChain-Anthropic도 있지만, Analyst Agent에서는 프롬프트를 정밀하게 제어해야 하므로(JSON-only 응답 강제, 토큰 제한, temperature 미사용) SDK 직접 호출이 더 적합했다.

### Layer 2: Agent Orchestration — `langgraph` + `langgraph-prebuilt` + `langgraph-checkpoint`

3개 AI 에이전트를 **순차 파이프라인**으로 연결하는 오케스트레이션 레이어.

```
[Data Agent] ──MarketData──> [News Agent] ──NewsData──> [Analyst Agent] ──AnalysisResults──> [Persist]
```

| 패키지 | 역할 | 프로젝트 기여 |
|--------|------|-------------|
| **langgraph** | StateGraph 정의, 노드 실행 순서 제어 | `graph.ainvoke()` 한 줄로 전체 파이프라인 비동기 실행. 에이전트 간 데이터를 `MarketAnalysisState` TypedDict로 안전하게 전달 |
| **langgraph-prebuilt** | 사전 정의된 노드/에지 패턴 | 보일러플레이트 코드 절감. 조건부 분기, 에러 핸들링 패턴 재사용 |
| **langgraph-checkpoint** | 실행 중간 상태 저장 | 배치가 News Agent에서 실패해도, Data Agent 결과는 보존. 실패 지점부터 재시도 가능 |

**왜 LangGraph인가?** 단순 함수 체이닝 대신 LangGraph를 선택한 이유:
1. **상태 격리** — 한 에이전트 크래시가 전체 파이프라인을 오염시키지 않음
2. **디버깅** — 각 노드의 입출력을 독립적으로 검사 가능
3. **확장성** — 새 에이전트(예: Sentiment Agent) 추가 시 그래프에 노드만 삽입

### Layer 3: LLM Abstraction — `langchain-core` + `langchain-anthropic` + `langchain`

LangGraph 노드 내부의 기반 인프라를 제공하는 추상화 레이어.

| 패키지 | 역할 | 프로젝트 기여 |
|--------|------|-------------|
| **langchain-core** | `RunnableConfig`, TypedDict 상태, 체인 인터페이스 | Analyst Agent의 `config` 파라미터로 Settings 주입, 테스트 시 mock 용이 |
| **langchain-anthropic** | Claude 모델을 LangChain 인터페이스로 래핑 | 향후 GPT-4o, Gemini 등으로 모델 교체 시 이 레이어만 변경 (provider 추상화) |
| **langchain** | 체인 구성, 도구 통합, 프롬프트 템플릿 | LangGraph와 LangSmith 연동의 기반 |

### Observability — `langsmith` + `langgraph-sdk`

| 패키지 | 역할 | 프로젝트 기여 |
|--------|------|-------------|
| **langsmith** | 에이전트 호출 트레이싱 (입출력, 지연시간, 토큰 비용) | "왜 이 배치에서 10개 시그널이 나왔지?" → 트레이스에서 Step 2 필터 통과 후보 확인 → 임계값 조정 |
| **langgraph-sdk** | LangGraph 서버 모드 연동 | 현재 인프로세스 실행이지만, 향후 파이프라인 분리 배포 시 활용 |

### AI 패키지 의존성 계보

```
anthropic (Claude API 직접 호출)
    ↑
langchain-anthropic (LangChain ↔ Anthropic 브릿지)
    ↑
langchain-core (RunnableConfig, State, Chain interface)
    ↑
langgraph (StateGraph 정의, 노드 실행)
    ├── langgraph-prebuilt (공통 에이전트 패턴)
    ├── langgraph-checkpoint (상태 체크포인팅)
    └── langgraph-sdk (서버 모드 SDK)
    ↑
langsmith (실행 트레이싱, 관측성)
```

---

## Claude Code Skills — 개발 과정에서의 역할 상세

이 프로젝트는 **Claude Code** (Anthropic의 CLI AI 코딩 에이전트, Opus 4.6 1M context)로 개발되었다. 4일간 113+ 커밋, 5개 Phase를 완주하는 과정에서 **Superpowers Plugin Skills**가 핵심 워크플로우 역할을 했다.

### CLAUDE.md — 프로젝트 컨텍스트 주입

프로젝트 루트에 `CLAUDE.md` 파일로 Claude Code에게 프로젝트 컨텍스트를 제공:

- 프로젝트 개요, 기술 스택, 디렉터리 구조
- 코딩 컨벤션 (Python: type hints, async/await / TypeScript: strict mode)
- Git 컨벤션 (conventional commits)
- 환경변수 목록
- 주요 참조 문서 경로

### .claude/rules/ — 도메인별 규칙 파일

| 파일 | 내용 |
|------|------|
| `agent-prompts.md` | Analyst Agent 프롬프트 규칙 (Regime Matrix, Output 형식, Hallucination 방지) |
| `backend.md` | Python 컨벤션, FastAPI 패턴, LangGraph 상태 관리, Playwright 제한 |
| `frontend.md` | TypeScript strict, 컴포넌트 구조, 차트 유형, 디자인 토큰, 색상 체계 |

### `superpowers:brainstorming` — 기능 설계의 출발점

모든 주요 기능의 설계는 brainstorming 스킬에서 시작되었다. 이 스킬은 코드를 바로 작성하는 대신, **사용자의 의도를 파악하고 → 요구사항을 정리하고 → 설계 대안을 탐색한 후 → 합의된 방향으로 구현**하는 흐름을 강제한다.

**대표적 사용 사례:**
- **대시보드 4-Area 레이아웃 설계**: "섹터 로테이션 대시보드"라는 추상적 요구를 Macro Header / Sector Heatmap / News Feed / Deep Dive Chart 4영역으로 구체화
- **AI 3-Step Validation 설계**: 단순히 "AI로 분석하자"가 아니라, Macro → RS+Momentum → Claude Final의 3단계 검증 파이프라인으로 구조화
- **글로벌 위기 파이프라인**: ReliefWeb API 선정, Claude AI 필터링 기준, 대시보드 통합 방안까지 사전 설계

**핵심 기여:** "무엇을 만들지"와 "어떻게 만들지"를 분리. 구현에 뛰어들기 전에 설계를 확정했기 때문에, 후반부 대규모 리팩토링이 거의 없었다.

### `superpowers:writing-plans` — 5-Phase 구현 로드맵 수립

brainstorming에서 도출된 설계를 **단계별 구현 계획**으로 전환하는 스킬.

```
Phase 1: 기반 (모델, 서비스, 설정)
  ↓
Phase 2: AI 파이프라인 (LangGraph 3-Agent)
  ↓
Phase 3: API + 스케줄러 (FastAPI, APScheduler)
  ↓
Phase 4: 프론트엔드 (4a: Scaffold → 4b: Area B+C → 4c: Area D)
  ↓
Phase 5: 통합 + 배포 (Docker, Render, E2E 테스트)
```

**핵심 기여:**
- 각 Phase의 **산출물, 의존성, 검증 기준**을 미리 정의하여 작업 순서 최적화
- Phase 4를 4a→4b→4c로 세분화하여 프론트엔드 병렬 작업 가능하게 설계
- 전체 스펙 문서(`docs/superpowers/specs/`)를 자동 생성하여 세션 간 컨텍스트 유지

### `superpowers:executing-plans` — 계획의 체계적 실행

writing-plans에서 만든 로드맵을 **실제 코드로 전환**하는 실행 스킬. 각 단계를 TaskCreate로 등록하고, 완료 시 TaskUpdate로 체크하며, 리뷰 체크포인트에서 사용자와 합의하는 흐름을 따른다.

**핵심 기여:**
- Phase 1~5를 **4일 만에 113+ 커밋**으로 완주
- 각 Phase 완료 시점에 리뷰를 거쳐 다음 Phase의 방향 조정
- "이 작업은 뭐부터 해야 하지?" 고민 없이 계획대로 순차 실행

### `superpowers:systematic-debugging` — 버그의 체계적 추적

디버깅 스킬은 **증상 → 가설 → 검증 → 수정**의 구조화된 프로세스를 강제한다.

**이 프로젝트에서 해결한 주요 버그들:**

| 버그 | 증상 | 원인 | 해결 |
|------|------|------|------|
| EODHD API 402 | 모든 API 호출 실패 | 무료 티어 전면 유료 전환 | Yahoo Finance 전환 결정 |
| Supabase HTTP/2 끊김 | 간헐적 ConnectionTerminated | Supabase 서버측 HTTP/2 리셋 | `_safe_execute()` 재시도 래퍼 |
| Yahoo NaN 처리 | ^TNX Volume이 NaN | 인덱스 심볼은 거래량 없음 | NaN 필터링 추가 |
| 섹터 중복 표시 | 같은 섹터가 2번 | `symbol` vs `etf_symbol` 키 불일치 | dedup 로직 키 수정 |
| CORS 521 에러 | 로그인 실패 | Render 서버 다운 + CORS origin 미등록 | 서버 재시작 + origin 추가 |
| 시그널 과잉 (10건) | 모든 섹터에 regime_shift | 사전 필터 임계값 0.2 너무 낮음 | v2: 임계값 0.4 + 3개 제한 |

### `superpowers:verification-before-completion` — "됐다"고 말하기 전 검증

작업 완료를 선언하기 전에 **실제로 동작하는지 검증**하는 스킬. 테스트 실행, 빌드 확인, 실제 API 호출 등을 강제한다.

**검증 사례:**
- 매 Phase 완료 시 `pytest` 실행 (최종 77+ 테스트 통과)
- 파이프라인 구현 후 `curl -X POST /api/analysis/trigger` 실제 E2E 검증
- 프론트엔드 빌드 후 `npm run build` + `tsc --noEmit` 타입 체크
- Render 배포 후 실제 URL 접속 + Playwright MCP로 브라우저 테스트

### `document-skills:frontend-design` — 금융 대시보드 UI 품질

프론트엔드 컴포넌트를 만들 때 **디자인 품질을 보장**하는 스킬. "AI가 만든 티 나는" 제네릭 UI가 아니라, 금융 대시보드에 맞는 전문적 디자인을 구현하는 데 기여했다.

**적용 사례:**
- **Dark Theme 금융 대시보드**: `bg-slate-900` 기반 + 상승(green-500)/하락(red-500) 색상 체계
- **52주 범위 Bullet Chart**: 어두운 회색 트랙 + emerald 진행률 바 + 흰색 현재가 마커
- **스파크라인**: AreaChart + 그라데이션 + Y축 동적 스케일링 (flatline 해결)
- **AI Event Signals**: 카드 기반 UI + ScoreBar + 펄스 인디케이터
- **국면 배지**: Goldilocks(green), Reflation(amber), Stagflation(red), Deflation(blue) 색상 매핑

### `document-skills:webapp-testing` — Playwright 브라우저 테스트

배포된 웹 앱을 **실제 브라우저에서 테스트**하는 스킬. Playwright MCP를 통해 실제 사용자처럼 페이지를 탐색하고, 접근성 스냅샷을 캡처하여 UI 상태를 확인한다.

**이번 프로젝트에서의 사용:**
- Cloudflare 배포 후 로그인 페이지 접속 테스트
- `admin` 계정으로 로그인 시도 → CORS 에러 실시간 발견
- 브라우저 콘솔 에러 로그 분석으로 정확한 원인 파악 (preflight 요청 차단)

### `superpowers:dispatching-parallel-agents` — 병렬 작업 가속

독립적인 작업을 **여러 서브에이전트에 동시 분배**하여 개발 속도를 높이는 스킬. 한 에이전트가 백엔드를 구현하는 동안 다른 에이전트가 프론트엔드를 구현하는 식으로 병렬 처리한다.

### `superpowers:finishing-a-development-branch` — 작업 마무리 절차

구현 완료 후 **커밋 → 푸시 → 배포까지의 마무리 절차**를 가이드하는 스킬. conventional commit 메시지 작성, 변경 파일 리뷰, 불필요한 파일 제외 등을 체계적으로 수행한다.

### Skills 워크플로우 요약

```
brainstorming (설계)
  ↓
writing-plans (계획)
  ↓
executing-plans (실행)
  ├── frontend-design (UI 구현)
  ├── dispatching-parallel-agents (병렬 처리)
  └── systematic-debugging (버그 수정)
  ↓
verification-before-completion (검증)
  ↓
webapp-testing (브라우저 테스트)
  ↓
finishing-a-development-branch (마무리)
```

### 개발 통계

| 항목 | 수치 |
|------|------|
| 개발 기간 | 4일 (2026-04-05 ~ 2026-04-08) |
| 총 커밋 | 113+ |
| 백엔드 테스트 | 77+ |
| 프론트엔드 컴포넌트 | 21개 |
| API 엔드포인트 | 14개 |
| AI 에이전트 | 3개 (Data, News, Analyst) |
| DB 테이블 | 10+ |
| Supabase 마이그레이션 | 3개 |
| 사용된 Claude Code Skills | 9개 |

---

## Dependencies

### Backend (Python)

```
# Core Framework
fastapi>=0.115.0          # REST API
uvicorn[standard]>=0.30.0 # ASGI server (watchfiles, uvloop, httptools)
pydantic>=2.0.0           # Data validation
pydantic-settings>=2.0.0  # Environment management

# AI & LLM
langgraph>=0.4.0          # Agent orchestration (StateGraph)
langchain>=0.3.0          # LLM framework
langchain-anthropic>=0.3.0 # Claude integration
anthropic>=0.40.0         # Claude API SDK

# Data
yfinance>=0.2.40          # Yahoo Finance (free market data)
httpx>=0.27.0             # Async HTTP client
feedparser>=6.0.0         # RSS parsing

# Database
supabase>=2.0.0,<2.10.0   # PostgreSQL client

# Scheduling
apscheduler>=3.10.0,<4.0.0 # Background scheduler

# Utilities
python-dotenv>=1.0.0      # .env loader
aiofiles>=24.0.0          # Async file I/O
tzdata>=2024.1            # Timezone data
```

### Frontend (Node.js)

```
# Core
react@^19.2.4             # UI library
react-dom@^19.2.4         # DOM renderer
recharts@^3.8.1           # Charts (Treemap, BarChart, AreaChart)

# Styling
tailwindcss@^4.2.2        # CSS framework (v4, CSS-first)
@tailwindcss/vite@^4.2.2  # Vite plugin

# UI Components
class-variance-authority@^0.7.1  # Variant styling (Badge)
clsx@^2.1.1               # Conditional classes
tailwind-merge@^3.5.0     # Tailwind class merge
lucide-react@^1.7.0       # Icons

# Build
vite@^8.0.1               # Build tool
@vitejs/plugin-react@^6.0.1 # React plugin
typescript@~5.9.3         # Type system
```

### Transitive Dependencies (주요)

yfinance가 설치하는 주요 하위 의존성:

```
numpy, pandas             # 데이터 처리
beautifulsoup4            # HTML 파싱
requests                  # HTTP (yfinance 내부)
curl_cffi                 # cURL 기반 HTTP
peewee                    # 캐시 DB
frozendict                # 불변 딕셔너리
multitasking              # 병렬 다운로드
```

LangGraph/LangChain이 설치하는 주요 하위 의존성:

```
langsmith                 # 추적/모니터링
langgraph-sdk             # LangGraph 클라이언트
langgraph-checkpoint      # 상태 체크포인트
langgraph-prebuilt        # 프리빌트 에이전트
langchain-core            # 코어 추상화
```

Supabase가 설치하는 주요 하위 의존성:

```
gotrue                    # Auth 클라이언트
postgrest                 # REST API 클라이언트
realtime                  # WebSocket 클라이언트
storage3                  # Storage 클라이언트
supafunc                  # Edge Functions 클라이언트
```

---

## Quick Start

### 사전 요구사항

- Python 3.12+
- Node.js 22+
- API 키: Anthropic, NewsAPI.org, Supabase

### 1. 환경 변수 설정

```bash
cp backend/.env.example backend/.env
# backend/.env 편집하여 API 키 입력
```

### 2. Supabase 테이블 생성

Supabase SQL Editor에서 `backend/supabase/migrations/001_initial_schema.sql` 실행.

### 3. 설치 & 빌드

```bash
# Backend
cd backend
python -m venv .venv
.venv/Scripts/pip install -e ".[dev]"   # Windows
# .venv/bin/pip install -e ".[dev]"     # Mac/Linux

# Frontend
cd ../frontend
npm install
npm run build
```

### 4. 서버 실행

```bash
cd backend
.venv/Scripts/python -m uvicorn app.main:app --port 8000
```

### 5. 접속

1. `http://localhost:8000` 접속
2. 허용된 이름 입력 (ALLOWED_USERS에 등록된 이름)
3. 대시보드 진입

### 6. 데이터 수집 (최초)

```bash
curl -X POST http://localhost:8000/api/analysis/trigger \
  -H "X-API-Key: your-trigger-key"
```

이후 스케줄러가 매일 08:30/17:00 ET에 자동 실행.

---

## Deployment

### Docker

```bash
docker build -t economi-analyzer .
docker run -p 8000:8000 --env-file backend/.env economi-analyzer
```

**Dockerfile 특징:**
- 멀티 스테이지 빌드 (Node 22 Alpine + Python 3.12 Slim)
- `pip install --no-cache-dir backend/` — pyproject.toml 기반
- Frontend dist를 FastAPI가 정적 서빙
- Single worker (APScheduler in-process)

### Render

`render.yaml` 기반 자동 배포. Git push -> Auto-Deploy.

```yaml
services:
  - type: web
    name: economi-analyzer
    runtime: docker
    healthCheckPath: /health
```

**배포 URL:** https://sector-analyzer.onrender.com

**주의:** 무료 티어는 15분 비활성 시 Sleep, 첫 요청 50초+ 지연.

---

## Environment Variables

| 변수 | 필수 | 설명 |
|------|------|------|
| `ANTHROPIC_API_KEY` | Y | Claude API 키 |
| `NEWSAPI_KEY` | Y | NewsAPI.org 키 |
| `SUPABASE_URL` | Y | Supabase 프로젝트 URL |
| `SUPABASE_SERVICE_KEY` | Y | Supabase 서비스 키 |
| `TRIGGER_API_KEY` | Y | 수동 파이프라인 트리거 보호 |
| `ALLOWED_USERS` | N | 로그인 허용 사용자 (쉼표 구분, 기본: admin) |
| `CORS_ORIGINS` | N | 추가 CORS 허용 도메인 |
| `EODHD_API_KEY` | N | EODHD 키 (레거시, 현재 미사용) |

---

## Sector ETF List

| ETF | 섹터 (한글) | 주요 구성종목 (Top 5) |
|-----|------------|---------------------|
| XLF | 금융 | JPM, BRK-B, V, MA, BAC |
| XLRE | 부동산 | PLD, AMT, EQIX, CCI, PSA |
| XLK | 기술 | AAPL, MSFT, NVDA, AVGO, CRM |
| XLC | 커뮤니케이션 | GOOGL, META, NFLX, DIS, CMCSA |
| XLY | 경기소비재 | AMZN, TSLA, HD, MCD, NKE |
| XLI | 산업재 | CAT, UNP, HON, GE, RTX |
| XLB | 소재 | LIN, APD, SHW, ECL, FCX |
| XLE | 에너지 | XOM, CVX, COP, EOG, SLB |
| XLU | 유틸리티 | NEE, SO, DUK, CEG, SRE |
| XLV | 헬스케어 | UNH, JNJ, LLY, PFE, ABT |
| XLP | 필수소비재 | PG, KO, PEP, COST, WMT |

---

## Charts & Visualizations

| 차트 | 라이브러리 | 컴포넌트 | 설명 |
|------|----------|---------|------|
| Sector Heatmap | Recharts Treemap | `SectorHeatmap` | Volume 기반 크기, 7단계 색상 |
| Sub-Treemap | Recharts Treemap | `SectorStockTreemap` | 구성종목 15 + ETC |
| Sparkline | Recharts AreaChart | `SectorSparkline` | 30일 추세, 그라데이션 fill |
| Momentum Bar | Recharts BarChart (Grouped) | `MomentumBar` | 1W/1M/3M/1Y 4색 막대 |
| Relative Strength | Recharts BarChart | `RelativeStrength` | RS vs SPY, 조건부 색상 |
| 52W Range | Custom SVG (Bullet) | `RangeChart` | Min-Current-Max 불릿 차트 |
| AI Signals | Custom Cards | `EventMarker` | MAJOR/ALERT/WATCH 등급, 확신도 바 |

### 디자인 토큰

| 용도 | 색상 |
|------|------|
| 상승 (Bullish) | `#22c55e` (green-500) |
| 하락 (Bearish) | `#ef4444` (red-500) |
| Goldilocks 국면 | green-500 |
| Reflation 국면 | amber-500 |
| Stagflation 국면 | red-500 |
| Deflation 국면 | blue-500 |
| Impact 1~3 | gray |
| Impact 4~6 | amber |
| Impact 7~10 | red |
| 배경 | `#0f172a` (slate-900) |

---

## Caching Strategy

### Backend (Server-side)

| 대상 | 방식 | TTL | 위치 |
|------|------|-----|------|
| Sector Stocks | In-memory dict | 4시간 | `market.py` |
| Global Crises | Function attribute | 1시간 | `news.py` |
| DB 데이터 | Supabase + dedup 쿼리 | 파이프라인 주기 | `supabase.py` |

### Frontend (Client-side)

| 대상 | 방식 | TTL | 키 |
|------|------|-----|-----|
| Sector Stocks | localStorage | 4시간 | `sector_stocks_{etf}` |
| Market Movers | localStorage | 4시간 | `market_movers_{etf}` |
| Sparkline | localStorage | 4시간 | `sparkline_all` |

---

## Development

### 백엔드

```bash
cd backend
pip install -e ".[dev]"
uvicorn app.main:app --reload      # 개발 서버 (hot reload)
pytest                              # 테스트 실행
ruff check .                        # 린트
```

### 프론트엔드

```bash
cd frontend
npm install
npm run dev                         # Vite dev server (HMR)
npm run build                       # 프로덕션 빌드
npm run preview                     # 빌드 결과 미리보기
```

### 수동 파이프라인 트리거

```bash
curl -X POST http://localhost:8000/api/analysis/trigger \
  -H "X-API-Key: your-trigger-key"
```

---

## Changelog (2026-04-11)

### 대시보드 2탭 레이아웃 분리 — "시장 현황" / "AI 인사이트"

Yahoo Finance raw data와 AI 파이프라인 판단 결과를 **정보 레이어 단위로 분리**하는 대규모 UI 리팩토링.

**구조 변화:**
- 기존 Area A/B/C/D 단일 페이지 → **Sticky 헤더 + 2탭 구조**
- `GlobalMacroHeader` + `DashboardTabs`가 `sticky top-0 z-40`으로 고정
- 탭 선택은 `useStickyState` 커스텀 훅으로 **localStorage 영속** (lazy initializer로 first-paint flash 방지)
- `selectedSector`는 `Dashboard` 레벨 공유 state — 탭 전환 시 섹터 선택 유지
- 데이터 훅은 최상위에서 1회 호출, 두 탭이 같은 데이터 공유 (단일 진실 원천)

**Tab 1 "시장 현황" (7-Row MarketTab):**
1. `SectorHeatmap` (풀폭)
2. `SectorStockTreemap` (풀폭으로 확장 — 기존 좁은 컬럼에서 라벨 가독성 문제 해결)
3. `SectorSparkline` + `NewsImpactFeed` (2열)
4. `MarketMovers` + `EconomicCalendar` (2열)
5. `RelativeStrength` (풀폭)
6. `MomentumBar` (풀폭)
7. `RangeChart` (풀폭)

**Tab 2 "AI 인사이트" (3-Row AiTab):**
1. `BusinessCycleClock` + `RelativeRotationGraph` (2열, 맥락 설정)
2. `AiRotationSignals` (풀폭, 판단)
3. `AiScreenerTable` (풀폭, 실행 후보)

### 신규 파일 (5)

- `frontend/src/hooks/useStickyState.ts` — localStorage 영속 제네릭 훅 (lazy initializer)
- `frontend/src/components/layout/DashboardTabs.tsx` — WAI-ARIA tablist 탭 바
- `frontend/src/components/layout/MarketTab.tsx` — 7-Row 시장 현황 패널
- `frontend/src/components/layout/AiTab.tsx` — 3-Row AI 인사이트 패널
- `frontend/src/components/chart/AiRotationSignals.tsx` — `EventMarker` 경량 래퍼 (AI 시그널 전용 기능 확장 포인트)

### 파일 이동/리네임 (2, `git mv`)

- `components/header/BusinessCycleClock.tsx` → `components/chart/BusinessCycleClock.tsx` (Tab 2에서 사용되므로 의미 정합성)
- `components/chart/MultiChartGrid.tsx` → `components/chart/SectorComparisonCharts.tsx` (내부에서 `EventMarker` 제거, 3차트 세로 스택으로 단순화)

### 주요 수정

- **타입 인터페이스 도입:** `MarketDataState`/`NewsDataState`/`AnalysisDataState` + `DashboardTab` 유니언. 레이아웃 컴포넌트가 훅 모듈을 직접 import하지 않도록 분리 (layout → types 단방향)
- **`BusinessCycleClock` 확대:** 시계 컨테이너 240×240 → 360×360, quadrants 116 → 174, pointer 80 → 120 (비율 유지), 내부 텍스트/아이콘 사이즈 비례 확대
- **`EventMarker` 전면 재구성:** click-expand 토글 제거 (useState + isExpanded 삭제), button → div. `reasoning`이 1행 flex 컨테이너 우측(날짜 바로 왼쪽)에 **항상 표시**, `flex-1`로 남은 공간 최대 활용, `text-sm`/`text-white`/bullet 프리픽스로 가독성 개선
- **`MarketTab` 레이아웃 조정:** Row 3/4에서 `NewsImpactFeed`와 `MarketMovers` 위치 swap
- **`RelativeStrength` 라벨 수정:** 깨진 `hsl(var(--muted-foreground))` CSS 변수 fallback 제거, 흰색(`#ffffff`)으로 고정. 양수 바는 외부 상단(`y - 5`), 음수 바는 내부 zero-line 아래(`y + 14`)에 배치
- **`RelativeRotationGraph` 축 색상 수정:** 동일한 CSS 변수 fallback 버그로 tick이 검은색으로 렌더되던 문제 해결 (`var(--color-muted-foreground)` 직접 참조). 축 tick에 `tickFormatter` 추가해 소수점 2자리 고정

### 빌드/배포 인프라

- `frontend/vite.config.ts`에 Cloudflare Vite plugin 통합
- `frontend/.gitignore`에 `.wrangler`, `.dev.vars*`, `.env*` 규칙 추가
- `frontend/.env.production` (git ignored) 도입 — `VITE_API_URL=https://sector-analyzer.onrender.com/api` 빌드 타임 주입
- `LoginGate` 네트워크 에러 graceful handling: 서버 연결 실패 시 사용자 친화적 에러 메시지
- Scheduler에 `market_open` 배치 job 추가 (10:00 ET)

### 배포 워크플로

- Cloudflare Workers static assets (`not_found_handling: single-page-application`)
- `npm run deploy` = `npm run build && wrangler deploy`
- Worker URL: https://sectoranalyzerfrontend2026.kopserf.workers.dev

### 방법론

본 리팩토링은 **Superpowers skill 워크플로**(brainstorming → writing-plans → subagent-driven-development)로 진행:
1. `docs/superpowers/specs/2026-04-11-dashboard-tab-layout-design.md` — 스펙 작성 + spec-document-reviewer 2회 리뷰 루프
2. `docs/superpowers/plans/2026-04-11-dashboard-tab-layout.md` — 10-Task 구현 플랜 + plan-document-reviewer 리뷰
3. Task별 fresh 서브에이전트 dispatch + spec compliance/code quality 2단계 리뷰 후 커밋

---

## Changelog (2026-04-09)

### DB 캐싱 전환 — 실시간 외부 API 호출 제거

- **뉴스 요약 (summaries):** 매 요청마다 Claude API를 호출하던 방식에서, 파이프라인 배치 실행 시 AI 분석 결과를 `news_summaries` 테이블에 저장하고 API는 DB에서만 읽도록 전환
- **글로벌 위기 (crises):** Google News RSS + Claude 실시간 필터링을 제거, 파이프라인에서 `global_crises` 테이블에 미리 저장
- **Rotation Signals 버그 수정:** `_persist_results`에서 `batch_type` 변수 스코프 오류로 signals가 DB에 저장되지 않던 문제 해결
- **프론트엔드 localStorage 캐싱:** 모든 데이터 훅 (`useMarketData`, `useNewsData`, `useAnalysisData`)에 TTL 1시간 localStorage 캐싱 적용 (기존 SectorStockTreemap 패턴 확장)
- **Supabase 신규 테이블:** `news_summaries`, `global_crises`

### 신규 위젯

- **Business Cycle Clock:** 4국면(Goldilocks/Reflation/Stagflation/Deflation) 원형 시계 위젯. Framer Motion 포인터 애니메이션, Lucide 아이콘, 국면별 확률(%) 표시 및 추천 섹터 라벨
- **Relative Rotation Graph (RRG):** RS-Ratio(X) x RS-Momentum(Y) 4분면 scatter chart. 섹터별 ETF 심볼 LabelList 자동 표시, Leading/Improving/Weakening/Lagging 사분면 배경색 구분

### UI/UX 개선

- **Heatmap ↔ AI Screener 연동:** Heatmap 클릭 시 AI Screener 테이블 해당 행 하이라이트, 테이블 행 클릭 시 Heatmap 섹터 선택 동기화
- **모멘텀 기간 토글:** 1D/1W/1M/3M/6M/1Y 버튼으로 표시할 기간을 자유롭게 선택 (기본: 1W/1M/3M/1Y)
- **상대 강도 수치 라벨:** 막대 방향 끝(양수 위, 음수 아래)에 ±n.n% 수치 표시
- **Treemap 회사명 표시:** 종목코드 아래에 회사명 앞 7글자를 작은 글씨로 추가 표기
- **AI Rotation Signal 한글명:** 섹터 ETF 심볼 옆에 한글 섹터명 표시
- **뉴스 날짜 NaN 수정:** `published_at` 없는 경우 `analyzed_at` fallback

### 종목 회사명 정적 매핑

- **STOCK_NAMES:** 섹터당 20개, 총 200개 종목 풀네임을 정적 매핑 (`sector_stocks.py`)
- **Yahoo fallback:** 매핑에 없는 종목만 개별 `yf.Ticker().info` 조회 (rate limit 최소화)
- **DB 저장:** 파이프라인 실행 시 `sector_stocks.name`에 풀네임 저장

### localStorage 캐시 정책

- **매 정시(XX:00) flush:** TTL 기반에서 시각 기준 만료로 변경. 매 시 정각에 모든 캐시가 만료되어 DB에서 새로 fetch

---

## Disclaimer

**본 분석은 AI의 추론이며, 실제 투자 판단의 근거로 사용할 수 없습니다.**

모든 투자 결정은 본인의 판단과 책임 하에 이루어져야 합니다. 이 대시보드는 교육 및 연구 목적으로 제작되었습니다.

---

## License

Private project.

---

*Built with Claude Code (Opus 4.6, 1M context) + Superpowers Plugin*
