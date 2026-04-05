# CLAUDE.md - AI-Driven Market Insights Dashboard

## Project Overview

시장의 섹터 순환매(Sector Rotation) 흐름을 선제적으로 포착하고 투자 인사이트를 제공하는 종합 미국 주식 대시보드. EODHD(금융 데이터) + NewsAPI(뉴스) → LangGraph AI 에이전트 파이프라인 → Next.js 대시보드.

## Tech Stack

- **Backend:** Python 3.12+, FastAPI, LangGraph, LangChain, APScheduler
- **Frontend:** Next.js 15, React 19, shadcn/ui, Tailwind CSS, Recharts
- **AI:** Claude API (Anthropic SDK)
- **DB:** Supabase (PostgreSQL)
- **Data:** EODHD API, NewsAPI.org, Google News RSS (fallback)
- **Scraping:** Playwright MCP (동적 SPA 데이터), Claude Vision (차트 스크린샷 분석)
- **Deploy:** Vercel (frontend), Railway/Render (backend)

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
├── frontend/          # Next.js 대시보드
│   └── src/
│       ├── app/       # Next.js App Router
│       ├── components/# UI 컴포넌트
│       ├── lib/       # 유틸리티
│       └── types/     # TypeScript 타입
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
- Next.js App Router (서버 컴포넌트 우선)
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
npm run dev
npm run build
```

## Constraints & Warnings

- NewsAPI 무료 한도: 100 req/일 (배치 캐싱 필수)
- AI 분석 결과는 투자 조언이 아님 — 면책 조항(Disclaimer) 항상 표시
- EODHD API 키 미발급 상태 — 개발 시작 전 발급 필요
- NewsAPI 키 미발급 상태 — 개발 시작 전 발급 필요
- Playwright MCP: 브라우저 렌더링은 수 초~수십 초 소요 — Heavy Track으로만 사용
- Anti-bot 차단 위험: 대형 금융 사이트 Cloudflare 등 봇 방어 → Stealth/프록시 우회 필요 가능
