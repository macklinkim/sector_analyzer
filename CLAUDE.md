# CLAUDE.md - AI-Driven Market Insights Dashboard

## Project Overview

시장의 섹터 순환매(Sector Rotation) 흐름을 선제적으로 포착하고 투자 인사이트를 제공하는 종합 미국 주식 대시보드. EODHD(금융 데이터) + NewsAPI(뉴스) → LangGraph AI 에이전트 파이프라인 → Vite + React SPA 대시보드.

## Tech Stack

- **Backend:** Python 3.12+, FastAPI, LangGraph, LangChain, APScheduler
- **Frontend:** Vite + React 19, shadcn/ui, Tailwind CSS, Recharts
- **AI:** Claude API (Anthropic SDK)
- **DB:** Supabase (PostgreSQL)
- **Data:** EODHD API, NewsAPI.org, Google News RSS (fallback)
- **Scraping:** Playwright MCP (동적 SPA 데이터), Claude Vision (차트 스크린샷 분석)
- **Deploy:** Railway/Render (FastAPI가 정적 프론트엔드도 서빙, 단일 배포) 또는 Vercel/Netlify (정적 SPA 분리 배포)

## Project Structure

```
economi_analyzer/
├── backend/           # FastAPI + LangGraph 파이프라인
│   ├── app/
│   │   ├── agents/    # LangGraph 에이전트 (data, news, analyst)
│   │   ├── api/       # FastAPI REST 엔드포인트
│   │   ├── mcp/       # NewsAPI MCP 서버 + Playwright 태스크 정의
│   │   ├── models/    # Supabase 테이블 스키마
│   │   ├── services/  # 외부 API 클라이언트
│   │   └── scheduler/ # APScheduler 배치 작업
│   └── tests/
├── frontend/          # Vite + React SPA 대시보드
│   └── src/
│       ├── App.tsx        # 루트 컴포넌트
│       ├── components/
│       │   ├── header/    # GlobalMacroHeader, TickerBar, RegimeBadge
│       │   ├── sector/    # SectorHeatmap, SectorSparkline, MarketMovers
│       │   ├── news/      # NewsImpactFeed, ImpactCard, EconomicCalendar
│       │   ├── chart/     # MultiChartGrid, PriceChart, RelativeStrength, MomentumBar, RangeChart, EventMarker
│       │   ├── screener/  # AiScreenerTable
│       │   └── ui/        # Skeleton 등 공통 UI
│       ├── lib/           # api.ts, utils.ts
│       └── types/         # TypeScript 타입
└── docs/              # 설계 문서, 전략 가이드
```

## Key Design Decisions

- **Monorepo**: backend + frontend 단일 레포
- **LangGraph**: Data Agent → News Agent → Analyst Agent 순차 실행
- **Macro Regime Matrix**: 2D(성장x물가) 4국면 기반 섹터 로테이션 분석
- **배치 처리**: 1일 2회 (Pre-Market 08:30 ET, Post-Market 17:00 ET)
- **NewsAPI 한도 관리**: 배치 캐싱 + Google News RSS fallback
- **도구 이원화**: Fast Track(API) / Heavy Track(Playwright MCP) 엄격 분리
- **Claude Vision**: Playwright 스크린샷 기반 차트/히트맵 실시간 시각 분석
- **대시보드 4 Area 구조**: A(Macro Header) + B(Sector Heatmap/Movers) + C(News/Calendar) + D(Deep Dive Chart/Screener)
- **차트**: Recharts + TradingView Lightweight Charts (선택), Multi-Chart Grid 2~4분할

## Important References

- `docs/sector-rotation-strategy.md` — 섹터 로테이션 전략 (국면 매트릭스, 섹터 매핑, 판단 로직)
- `docs/superpowers/specs/2026-04-05-market-insights-dashboard-design.md` — 전체 설계 스펙
- `draft.md` — 원본 PRD

## Code Conventions

### Python (backend)
- Python 3.12+, type hints 필수
- async/await 패턴 (FastAPI)
- pydantic v2 for validation & settings
- 환경변수는 `app/config.py`에서 `pydantic-settings`로 관리
- 테스트: pytest + pytest-asyncio

### TypeScript (frontend)
- TypeScript strict mode
- Vite + React SPA (CSR, SSR 불필요)
- shadcn/ui 컴포넌트 사용 (직접 UI 구현 최소화)
- 스타일: Tailwind CSS (인라인 스타일 금지)

### Git
- 커밋 메시지: conventional commits (feat:, fix:, docs:, refactor:)
- 브랜치: feature/<name>, fix/<name>

## Environment Variables

```env
# Backend (.env)
ANTHROPIC_API_KEY=       # Claude API
EODHD_API_KEY=           # EODHD 금융 데이터
NEWSAPI_KEY=             # NewsAPI.org
SUPABASE_URL=            # Supabase 프로젝트 URL
SUPABASE_SERVICE_KEY=    # Supabase 서비스 키
```

## Common Commands

```bash
# Backend
cd backend && pip install -e ".[dev]"
uvicorn app.main:app --reload
pytest

# Frontend
cd frontend && npm install
npm run dev        # Vite dev server
npm run build      # 정적 빌드 → dist/
npm run preview    # 빌드 결과 로컬 미리보기
```

## Constraints & Warnings

- NewsAPI 무료 한도: 100 req/일 (배치 캐싱 필수)
- Anti-bot 차단 위험: 대형 금융 사이트 Cloudflare 등 봇 방어 → Stealth/프록시 우회 필요 가능

💻 Windows Terminal Environment Summary
이 환경은 Windows이지만, Scoop을 통해 리눅스 표준 유틸리티와 고성능 Modern CLI가 구축되어 있습니다. 터미널 제어 및 스크립팅 시 다음 도구들을 우선 사용하십시오.

1. GNU/Linux Core Utilities
파일/텍스트: ls, cp, mv, rm, cat, grep, sed, awk (Gawk) 사용 가능.
네트워크: curl, wget.
권한/빌드: sudo, make.
에디터: vim, nvim (Neovim).

2. Modern CLI Alternatives (AI 우선 권장)
일반 명령어보다 아래의 고성능/가독성 도구를 사용하는 것을 선호합니다.
파일 탐색: eza (replaces ls), fd (replaces find).
내용 검색: rg (ripgrep, replaces grep).
파일 열람: bat (replaces cat, syntax highlighting 지원).
디렉토리 이동: z (zoxide, smart cd).
데이터 파싱: jq (JSON), yq (YAML).
모니터링: btop.
문서 확인: tldr (replaces man).

3. 기타 도구
Git: git, gh (GitHub CLI).
압축: 7zip.
검색: fzf (Fuzzy Finder).
프롬프트: starship.

⚠️ 주의사항
모든 경로는 가급적 POSIX 스타일(/)로 처리하십시오.
Windows CMD 또는 PowerShell 기반에서 실행되므로 복잡한 파이프라인 연산 시 환경 호환성을 고려하십시오.