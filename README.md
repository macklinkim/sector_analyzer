# AI-Driven Market Insights Dashboard

> **미국 주식 시장의 섹터 순환매(Sector Rotation) 흐름을 AI로 분석하고 투자 인사이트를 제공하는 종합 대시보드**

Yahoo Finance + NewsAPI + Google News RSS --> LangGraph AI 3-Agent Pipeline --> Claude AI 분석 --> FastAPI + React SPA 대시보드

**Live Demo:** https://sector-analyzer.onrender.com

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

```
+----------------------------------------------------------------+
|  [A] Global Macro Header                                        |
|  나스닥 21,879 +0.18% | 다우 46,504 -0.13% | S&P500 6,582 +0.11%|
|  WTI $110.14 | US10Y 4.31 | DXY 99.94 | Gold $4,705              |
|  현재 국면: Reflation (60%)                                       |
+-------------------------------+--------------------------------+
|  [B] Sector Analysis          |  [C] News & Indicators         |
|  +---------+                  |  News Impact Feed              |
|  | Sector  |                  |  [전체|경제|정치|사회|글로벌]     |
|  | Heatmap |                  |  뉴스 카드 + AI 한글 요약         |
|  | Treemap |                  |  [긍정 7/10 - 기술]              |
|  +---------+                  |  ─────────────────             |
|  섹터 구성종목 Treemap          |  Economic Calendar              |
|  + Sparkline (30일 추세)       |  Gold $4,705 (prev: 4,651)     |
|  + Market Movers              |  WTI $110.14 (prev: 111.54)    |
+-------------------------------+--------------------------------+
|  [D] Charts & AI Screener                                       |
|  AI Rotation Signals  |  상대 강도 vs S&P500                     |
|  [MAJOR] XLU +0.72    |  [BarChart: RS by sector]               |
|  [ALERT] XLE +0.58    |                                         |
|  ─────────────────────────────────────────                      |
|  섹터 모멘텀 (1W / 1M / 3M / 1Y)                                |
|  [Grouped BarChart: momentum by sector and period]              |
|  ─────────────────────────────────────────                      |
|  52주 범위 차트 (Bullet Chart)                                    |
|  ─────────────────────────────────────────                      |
|  AI Sector Screener Table                                       |
|  Rank | Sector | ETF | AI Score | Base | News | Mom | Signal   |
+----------------------------------------------------------------+
```

---

## Frontend Components

### Area A: Header

| 컴포넌트 | 파일 | 기능 |
|---------|------|------|
| `GlobalMacroHeader` | `header/GlobalMacroHeader.tsx` | Area A 전체 래퍼 |
| `TickerBar` | `header/TickerBar.tsx` | 지수 + 거시 지표 티커 (이름 매핑, 화살표) |
| `RegimeBadge` | `header/RegimeBadge.tsx` | 현재 국면 배지 (Goldilocks/Reflation/...) |

### Area B: Sector Analysis

| 컴포넌트 | 파일 | 기능 |
|---------|------|------|
| `SectorHeatmap` | `sector/SectorHeatmap.tsx` | Recharts Treemap, volume 기반 크기, 7단계 색상 |
| `SectorStockTreemap` | `sector/SectorStockTreemap.tsx` | 구성종목 Sub-Treemap (Top 15 + ETC), localStorage 4시간 캐시 |
| `SectorSparkline` | `sector/SectorSparkline.tsx` | 30일 AreaChart + 그라데이션, 번들 API 1회 호출 |
| `MarketMovers` | `sector/MarketMovers.tsx` | Top Gainers/Losers/Volume, localStorage 4시간 캐시 |

### Area C: News & Calendar

| 컴포넌트 | 파일 | 기능 |
|---------|------|------|
| `NewsImpactFeed` | `news/NewsImpactFeed.tsx` | 탭 필터 (전체/경제/정치/사회/글로벌) + CrisisCard |
| `ImpactCard` | `news/ImpactCard.tsx` | 뉴스 카드: 제목, AI 한글 요약, 임팩트 점수, 섹터 |
| `EconomicCalendar` | `news/EconomicCalendar.tsx` | 거시 지표 4개: US10Y, DXY, WTI, Gold |

### Area D: Charts & Screener

| 컴포넌트 | 파일 | 기능 |
|---------|------|------|
| `MultiChartGrid` | `chart/MultiChartGrid.tsx` | 레이아웃: Signals+RS(2col) -> Momentum(full) -> Range |
| `EventMarker` | `chart/EventMarker.tsx` | AI Rotation Signals: MAJOR/ALERT/WATCH 등급, 확신도 바 |
| `MomentumBar` | `chart/MomentumBar.tsx` | Grouped BarChart (1W/1M/3M/1Y), 커스텀 Legend |
| `RelativeStrength` | `chart/RelativeStrength.tsx` | BarChart (RS vs SPY), 조건부 색상 (녹/적) |
| `RangeChart` | `chart/RangeChart.tsx` | 52주 Bullet Chart (11 섹터, 5열 그리드) |
| `AiScreenerTable` | `screener/AiScreenerTable.tsx` | AI Score 기반 랭킹 테이블, Overweight/Neutral/Underweight |

### Common UI

| 컴포넌트 | 기반 | 기능 |
|---------|------|------|
| `LoginGate` | Custom | 허가제 로그인 게이트 |
| `LoadingScreen` | Custom | 로딩 모달 (반투명 배경 + 텍스트) |
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

## Claude Code Integration

### CLAUDE.md

프로젝트 루트에 `CLAUDE.md` 파일로 Claude Code에게 프로젝트 컨텍스트를 제공:

- 프로젝트 개요, 기술 스택, 디렉터리 구조
- 코딩 컨벤션 (Python: type hints, async/await / TypeScript: strict mode)
- Git 컨벤션 (conventional commits)
- 환경변수 목록
- 주요 참조 문서 경로

### .claude/rules/

| 파일 | 내용 |
|------|------|
| `agent-prompts.md` | Analyst Agent 프롬프트 규칙 (Regime Matrix, Output 형식, Hallucination 방지) |
| `backend.md` | Python 컨벤션, FastAPI 패턴, LangGraph 상태 관리, Playwright 제한 |
| `frontend.md` | TypeScript strict, 컴포넌트 구조, 차트 유형, 디자인 토큰, 색상 체계 |

### Superpowers Plugin Skills

| 스킬 | 용도 |
|------|------|
| `brainstorming` | 기능 설계 전 아이디어 탐색 |
| `writing-plans` | 구현 계획 작성 |
| `executing-plans` | 계획 기반 구현 |
| `test-driven-development` | TDD 워크플로우 |
| `systematic-debugging` | 체계적 디버깅 |
| `verification-before-completion` | 완료 전 검증 |
| `code-reviewer` | 코드 리뷰 에이전트 |
| `frontend-design` | 프론트엔드 디자인 |

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

## Disclaimer

**본 분석은 AI의 추론이며, 실제 투자 판단의 근거로 사용할 수 없습니다.**

모든 투자 결정은 본인의 판단과 책임 하에 이루어져야 합니다. 이 대시보드는 교육 및 연구 목적으로 제작되었습니다.

---

## License

Private project.

---

*Built with Claude Code (Opus 4.6, 1M context) + Superpowers Plugin*
