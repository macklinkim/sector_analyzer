# AI-Driven Market Insights Dashboard

미국 주식 시장의 섹터 순환매(Sector Rotation) 흐름을 AI로 분석하고 투자 인사이트를 제공하는 대시보드.

EODHD(금융 데이터) + NewsAPI(뉴스) -> LangGraph AI 파이프라인 -> FastAPI + React SPA 대시보드

## 주요 기능

- **Macro Regime Detection** -- 거시 경제 국면(Goldilocks/Reflation/Stagflation/Deflation) 자동 판정
- **Sector Heatmap** -- 11개 섹터 ETF 등락률 Treemap + 구성종목 Treemap
- **News Impact Feed** -- 뉴스별 AI 한글 요약 + 섹터 임팩트 점수(0~10) + 카테고리 필터
- **AI Sector Screener** -- 국면 기반 섹터 점수 + 추천(Overweight/Neutral/Underweight)
- **차트** -- Sector Momentum(Grouped Bar), Relative Strength(Baseline Area), 52주 Range(Bullet)
- **자동 배치** -- 매일 2회(Pre-Market 08:30 ET, Post-Market 17:00 ET) 자동 분석
- **로그인** -- 허가제 이름 기반 접근 제어 (추후 정식 인증 연동 예정)
- **한글 UI** -- 섹터/지수/카테고리 한글 라벨 (i18n 언어팩)

## 기술 스택

| 영역 | 기술 |
|------|------|
| Backend | Python 3.12+, FastAPI, LangGraph, LangChain, APScheduler |
| Frontend | Vite, React 19, TypeScript (strict), Tailwind CSS v4, Recharts |
| AI | Claude API (Anthropic) -- 국면 분석 + 뉴스 요약 |
| DB | Supabase (PostgreSQL) |
| Data | EODHD API, NewsAPI.org |
| Deploy | Docker, Railway / Render |

## 프로젝트 구조

```
economi_analyzer/
├── backend/
│   ├── app/
│   │   ├── agents/              # LangGraph 에이전트 (data, news, analyst)
│   │   ├── api/routes/          # REST API (auth, market, news, analysis, health)
│   │   ├── scheduler/           # APScheduler 배치 작업
│   │   ├── services/            # EODHD, NewsAPI, Supabase, sector_stocks
│   │   └── models/              # Pydantic 스키마
│   ├── tests/                   # pytest (77 tests)
│   └── supabase/migrations/     # DB 스키마 SQL
├── frontend/
│   └── src/
│       ├── components/
│       │   ├── auth/            # LoginGate (로그인 게이트)
│       │   ├── header/          # GlobalMacroHeader, TickerBar, RegimeBadge
│       │   ├── sector/          # SectorHeatmap, SectorStockTreemap, Sparkline, Movers
│       │   ├── news/            # NewsImpactFeed, ImpactCard, EconomicCalendar
│       │   ├── chart/           # MultiChartGrid, MomentumBar, RelativeStrength, RangeChart
│       │   ├── screener/        # AiScreenerTable
│       │   └── ui/              # Skeleton, Badge, Card (shadcn/ui)
│       ├── hooks/               # useMarketData, useNewsData, useAnalysisData
│       ├── lib/                 # api.ts, utils.ts, i18n.ts
│       └── types/               # TypeScript 타입 정의
├── scripts/                     # 서버 시작/종료/재시작 스크립트
├── Dockerfile                   # 멀티 스테이지 빌드
├── railway.toml                 # Railway 배포 설정
└── render.yaml                  # Render 배포 설정
```

## 빠른 시작

### 사전 요구사항

- Python 3.12+
- Node.js 22+
- API 키: Anthropic, EODHD, NewsAPI.org, Supabase

### 1. 환경 변수 설정

```bash
cp backend/.env.example backend/.env
```

`backend/.env`를 편집하여 API 키 입력:

```env
ANTHROPIC_API_KEY=sk-ant-...       # Claude API
EODHD_API_KEY=...                  # EODHD 금융 데이터
NEWSAPI_KEY=...                    # NewsAPI.org
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_SERVICE_KEY=eyJ...
TRIGGER_API_KEY=your-secret-key    # 수동 파이프라인 트리거 보호용
ALLOWED_USERS=admin,mack           # 로그인 허용 사용자 (쉼표 구분)
```

### 2. Supabase 테이블 생성

Supabase SQL Editor에서 `backend/supabase/migrations/001_initial_schema.sql` 실행.

### 3. 설치

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
# 편의 스크립트 사용 (프로젝트 루트에서)
scripts/start.bat          # Windows: 서버 시작
scripts/stop.bat           # Windows: 서버 종료
scripts/restart.bat        # Windows: 재시작 (빌드 포함)

# 또는 직접 실행
cd backend
.venv/Scripts/python -m uvicorn app.main:app --port 8000
```

### 5. 대시보드 접속

1. `http://localhost:8000` 접속
2. 허용된 이름 입력 (예: `admin`, `mack`)
3. 대시보드 진입

### 6. 데이터 수집 (수동 트리거)

```bash
curl -X POST http://localhost:8000/api/analysis/trigger \
  -H "X-API-Key: your-secret-key"
```

스케줄러가 매일 2회 자동 실행하므로, 이후에는 수동 트리거 불필요.

## API 엔드포인트

| Method | Path | 설명 |
|--------|------|------|
| GET | `/health` | 헬스체크 |
| POST | `/api/auth/login` | 로그인 (name 기반) |
| GET | `/api/auth/verify` | 세션 검증 |
| GET | `/api/market/indices` | 주요 지수 (S&P500, NASDAQ, DOW, KOSDAQ) |
| GET | `/api/market/sectors` | 11개 섹터 ETF 데이터 (XLC 포함) |
| GET | `/api/market/indicators` | 경제 지표 (US10Y, DXY 등) |
| GET | `/api/market/regime` | 현재 매크로 국면 |
| GET | `/api/market/sector-stocks/{etf}` | 섹터 구성종목 Top 15 |
| GET | `/api/news/articles` | 뉴스 목록 (?category=business&limit=20) |
| GET | `/api/news/summaries` | AI 한글 요약 포함 뉴스 (?limit=15) |
| GET | `/api/news/impacts` | 뉴스 임팩트 분석 |
| GET | `/api/analysis/report` | AI 분석 리포트 |
| GET | `/api/analysis/scoreboards` | 섹터 스코어보드 |
| GET | `/api/analysis/signals` | 로테이션 시그널 |
| POST | `/api/analysis/trigger` | 수동 파이프라인 실행 (X-API-Key 필요) |
| GET | `/docs` | Swagger UI |

## 섹터 목록 (11개)

| ETF | 섹터 (한글) | 주요 구성종목 |
|-----|------------|--------------|
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

## 배포

### Docker

```bash
docker build -t economi-analyzer .
docker run -p 8000:8000 --env-file backend/.env economi-analyzer
```

### Railway

```bash
railway up
```

환경변수를 Railway 대시보드에서 설정 필요.

### Render

`render.yaml` 기반 자동 배포. Git push 시 트리거.

## 대시보드 레이아웃

```
┌───────────────────────────────────────────────────────┐
│  [A] Global Macro Header                              │
│  S&P500 655.83 +0.09% | 나스닥 | 다우 | 코스닥        │
│  US10Y 4.25 | DXY | WTI | Gold                        │
│  현재 국면: Goldilocks (75%)  AI 분석중...              │
├────────────────────────┬──────────────────────────────┤
│  [B] Sector Heatmap    │  [C] News Impact Feed        │
│  Treemap (11섹터)       │  탭 [전체|경제|정치|사회|...]  │
│  ─────────────────     │  뉴스 + AI 한글 요약          │
│  Sector Top Stock      │  [긍정 7/10 · 기술]          │
│  Treemap (종목 10+etc)  │  ─────────────────          │
│  ─────────────────     │  Economic Calendar           │
│  Sparkline (날짜 포함)   │  ▲US10Y 4.25 (prev: 4.20)  │
│  + Market Movers       │                              │
├────────────────────────┴──────────────────────────────┤
│  [D] Charts + AI Screener                             │
│  Momentum Bar (1W/1M/3M) | Relative Strength          │
│  52주 Range (금융/부동산/기술/...)                       │
│  AI Sector Screener Table (Rank, Score, 추천)          │
└───────────────────────────────────────────────────────┘
```

## 면책 조항

본 분석은 AI의 추론이며, 실제 투자 판단의 근거로 사용할 수 없습니다. 모든 투자 결정은 본인의 판단과 책임 하에 이루어져야 합니다.

## License

Private project.
