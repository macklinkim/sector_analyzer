# AI-Driven Market Insights Dashboard

미국 주식 시장의 섹터 순환매(Sector Rotation) 흐름을 AI로 분석하고 투자 인사이트를 제공하는 대시보드.

EODHD(금융 데이터) + NewsAPI(뉴스) -> LangGraph AI 파이프라인 -> FastAPI + React SPA 대시보드

## 주요 기능

- **Macro Regime Detection** -- 거시 경제 국면(Goldilocks/Reflation/Stagflation/Deflation) 자동 판정
- **Sector Heatmap** -- 11개 섹터 ETF 등락률 Treemap 시각화
- **News Impact Feed** -- 뉴스별 섹터 임팩트 점수(1~10) AI 분석
- **AI Sector Screener** -- 국면 기반 섹터 점수 + 추천(Overweight/Neutral/Underweight)
- **자동 배치** -- 매일 2회(Pre-Market 08:30 ET, Post-Market 17:00 ET) 자동 분석

## 기술 스택

| 영역 | 기술 |
|------|------|
| Backend | Python 3.12+, FastAPI, LangGraph, LangChain |
| Frontend | Vite, React 19, TypeScript, Tailwind CSS v4, Recharts |
| AI | Claude API (Anthropic) |
| DB | Supabase (PostgreSQL) |
| Data | EODHD API, NewsAPI.org |
| Deploy | Docker, Railway / Render |

## 프로젝트 구조

```
economi_analyzer/
├── backend/                 # FastAPI + LangGraph 파이프라인
│   ├── app/
│   │   ├── agents/          # LangGraph 에이전트 (data, news, analyst)
│   │   ├── api/routes/      # REST API 엔드포인트
│   │   ├── scheduler/       # APScheduler 배치 작업
│   │   ├── services/        # 외부 API 클라이언트 (EODHD, NewsAPI, Supabase)
│   │   └── models/          # Pydantic 스키마
│   └── tests/               # pytest (77 tests)
├── frontend/                # Vite + React SPA
│   └── src/
│       ├── components/      # header, sector, news, chart, screener, ui
│       ├── hooks/           # useMarketData, useNewsData, useAnalysisData
│       ├── lib/             # api.ts, utils.ts
│       └── types/           # TypeScript 타입 정의
├── Dockerfile               # 멀티 스테이지 빌드
├── railway.toml             # Railway 배포 설정
└── render.yaml              # Render 배포 설정
```

## 시작하기

### 사전 요구사항

- Python 3.12+
- Node.js 22+
- API 키: Anthropic, EODHD, NewsAPI.org, Supabase

### 1. 환경 변수 설정

```bash
cp backend/.env.example backend/.env
```

`backend/.env`를 편집하여 API 키를 입력:

```env
ANTHROPIC_API_KEY=sk-ant-...       # Claude API
EODHD_API_KEY=...                  # EODHD 금융 데이터
NEWSAPI_KEY=...                    # NewsAPI.org
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_SERVICE_KEY=eyJ...
TRIGGER_API_KEY=your-secret-key    # 수동 파이프라인 트리거 보호용
```

### 2. Supabase 테이블 생성

Supabase SQL Editor에서 `backend/supabase/migrations/001_initial_schema.sql` 실행.

### 3. Backend 설치 + 실행

```bash
cd backend
python -m venv .venv
.venv/Scripts/pip install -e ".[dev]"   # Windows
# .venv/bin/pip install -e ".[dev]"     # Mac/Linux

# 테스트
.venv/Scripts/python -m pytest -v

# 서버 실행
.venv/Scripts/python -m uvicorn app.main:app --reload --port 8000
```

### 4. Frontend 빌드

```bash
cd frontend
npm install
npm run build     # dist/ 생성 -> FastAPI가 자동 서빙
```

### 5. 대시보드 접속

`http://localhost:8000` -- FastAPI가 API + SPA 모두 서빙

### 6. 데이터 수집 (수동 트리거)

```bash
curl -X POST http://localhost:8000/api/analysis/trigger \
  -H "X-API-Key: your-secret-key"
```

스케줄러가 자동으로 매일 2회 실행하므로, 이후에는 수동 트리거 불필요.

## API 엔드포인트

| Method | Path | 설명 |
|--------|------|------|
| GET | `/health` | 헬스체크 |
| GET | `/api/market/indices` | 주요 지수 (S&P500, NASDAQ, DOW) |
| GET | `/api/market/sectors` | 11개 섹터 ETF 데이터 |
| GET | `/api/market/indicators` | 경제 지표 (US10Y, DXY 등) |
| GET | `/api/market/regime` | 현재 매크로 국면 |
| GET | `/api/news/articles` | 뉴스 목록 (?category=business&limit=20) |
| GET | `/api/news/impacts` | 뉴스 임팩트 분석 |
| GET | `/api/analysis/report` | AI 분석 리포트 |
| GET | `/api/analysis/scoreboards` | 섹터 스코어보드 (?batch_type=pre_market) |
| GET | `/api/analysis/signals` | 로테이션 시그널 |
| POST | `/api/analysis/trigger` | 수동 파이프라인 실행 (X-API-Key 필요) |
| GET | `/docs` | Swagger UI |

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
┌─────────────────────────────────────────────────┐
│  [A] Global Macro Header                        │
│  S&P500 +0.09% | NASDAQ | DOW | US10Y | Gold   │
│  현재 국면: Goldilocks (75%)                     │
├──────────────────────┬──────────────────────────┤
│  [B] Sector Heatmap  │  [C] News Impact Feed    │
│  Treemap + Sparkline │  탭 [전체|경제|기술|...]   │
│  + Market Movers     │  + Economic Calendar     │
├──────────────────────┴──────────────────────────┤
│  [D] Charts + AI Screener                       │
│  MomentumBar | RelativeStrength | RangeChart    │
│  AI Sector Screener Table                       │
└─────────────────────────────────────────────────┘
```

## 면책 조항

본 분석은 AI의 추론이며, 실제 투자 판단의 근거로 사용할 수 없습니다. 모든 투자 결정은 본인의 판단과 책임 하에 이루어져야 합니다.

## License

Private project.
