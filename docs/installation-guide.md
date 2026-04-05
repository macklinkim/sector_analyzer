# Installation & Setup Guide

본 문서는 프로젝트 개발 환경 설정 및 필수 의존성 설치 가이드입니다.

---

## 1. 사전 준비 (Prerequisites)

### 필수 소프트웨어

| 도구 | 버전 | 설치 방법 (Windows/scoop) |
| :--- | :--- | :--- |
| Python | 3.12+ | `scoop install python` |
| Node.js | 20 LTS+ | `scoop install nodejs-lts` |
| Git | 최신 | `scoop install git` |
| jq | 최신 | `scoop install jq` (이미 설치됨) |

```bash
# scoop으로 일괄 설치
scoop install python nodejs-lts git
```

### Python 가상환경 도구 (택 1)

```bash
# uv (추천 - 빠른 패키지 관리자)
scoop install uv

# 또는 기본 venv
python -m venv .venv
```

---

## 2. API 키 발급

### 2-1. EODHD API

1. https://eodhd.com 접속 → 회원가입
2. 무료 플랜(Free) 또는 유료 플랜 선택
3. Dashboard → API Token 복사
4. 무료 플랜 제약: 일일 20회 호출, 지연 데이터(15~20분), 제한된 엔드포인트

> **참고:** 무료 플랜으로 개발을 시작하되, 섹터 ETF 12종 + 지수 3종 + 경제지표 조회를 고려하면 유료 플랜($19.99/월 Fundamentals)이 권장됩니다.

### 2-2. NewsAPI.org

1. https://newsapi.org 접속 → 회원가입
2. Get API Key 클릭
3. Developer 플랜 (무료): 100 req/일
4. API Key 복사

> **참고:** 개발 단계에서는 무료 플랜으로 충분합니다 (1일 2배치 x 4카테고리 = 8회).

### 2-3. Anthropic (Claude API)

1. https://console.anthropic.com 접속 → 계정 생성/로그인
2. API Keys → Create Key
3. 크레딧 충전 (사용량 기반 과금)
4. 모델: `claude-sonnet-4-20250514` 권장 (비용 효율)

### 2-4. Supabase

1. https://supabase.com 접속 → 프로젝트 생성
2. Settings → API → `Project URL` 복사
3. Settings → API → `service_role` key 복사 (비공개 키)
4. 무료 플랜: 500MB DB, 1GB 스토리지

---

## 3. 환경변수 설정

```bash
# backend/.env 파일 생성
cp backend/.env.example backend/.env
```

```env
# backend/.env
ANTHROPIC_API_KEY=sk-ant-xxxxx
EODHD_API_KEY=xxxxxxxx
NEWSAPI_KEY=xxxxxxxx
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_SERVICE_KEY=eyJxxxxx
```

> `.env` 파일은 `.gitignore`에 포함되어 있어 Git에 커밋되지 않습니다.

---

## 4. Backend 설치

### Python 의존성

```bash
cd backend

# uv 사용 시 (추천)
uv venv
uv pip install -e ".[dev]"

# 또는 기본 pip
python -m venv .venv
source .venv/bin/activate  # Windows Git Bash
pip install -e ".[dev]"
```

### 핵심 패키지 목록

```toml
# pyproject.toml [project.dependencies]
[project]
dependencies = [
    # Web Framework
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.30.0",

    # AI / Agent
    "langgraph>=0.4.0",
    "langchain>=0.3.0",
    "langchain-anthropic>=0.3.0",
    "anthropic>=0.40.0",

    # MCP
    "mcp>=1.0.0",

    # Data & API
    "httpx>=0.27.0",           # async HTTP client
    "feedparser>=6.0.0",       # Google News RSS fallback
    "supabase>=2.0.0",         # Supabase Python SDK

    # Scheduler
    "apscheduler>=3.10.0",

    # Config & Validation
    "pydantic>=2.0.0",
    "pydantic-settings>=2.0.0",
    "python-dotenv>=1.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.24.0",
    "pytest-cov>=5.0.0",
    "ruff>=0.6.0",             # linter + formatter
]
```

### MCP 서버 설정

```bash
# Anthropic Fetch MCP 설치
npm install -g @anthropic-ai/fetch-mcp

# 또는 npx로 실행 (설치 불필요)
npx @anthropic-ai/fetch-mcp
```

### Playwright MCP 설치

Playwright MCP는 ��적 금융 포털 스크래핑(Heavy Track)에 사용됩니다.

```bash
# Playwright MCP 서버 설치
npm install -g @anthropic-ai/playwright-mcp

# Playwright 브라우저 바이너리 설치 (최초 1회)
npx playwright install chromium

# 또는 npx로 실행 (설치 불필요)
npx @anthropic-ai/playwright-mcp
```

**Claude Code에서 MCP 서버 등록 (.mcp.json):**

```json
{
  "mcpServers": {
    "fetch": {
      "command": "npx",
      "args": ["@anthropic-ai/fetch-mcp"]
    },
    "playwright": {
      "command": "npx",
      "args": ["@anthropic-ai/playwright-mcp"]
    },
    "newsapi": {
      "command": "python",
      "args": ["-m", "app.mcp.news_server"],
      "cwd": "./backend"
    }
  }
}
```

> **주의:** Playwright는 브라우저 렌더링을 수행하므로 메모리 사용량이 높습니다 (Chromium 인스턴스당 ~200MB). 동시 실행 수를 제한하세요.

#### Anti-bot 차단 대비 (선택)

대형 금융 사이트의 봇 차단을 우회해야 할 경우:

```bash
# Playwright Stealth 플러그인 (Python)
pip install playwright-stealth

# 프록시 설정은 backend/.env에서 관리
# PLAYWRIGHT_PROXY_URL=http://proxy-host:port
```

---

## 5. Frontend 설치

```bash
cd frontend

# Vite + React 프로젝트 초기화 (최초 1회)
npm create vite@latest . -- --template react-ts

# 의존성 설치
npm install

# Tailwind CSS 설정
npm install -D tailwindcss @tailwindcss/vite

# shadcn/ui 초기화
npx shadcn@latest init

# 필요한 shadcn 컴포넌트 설치
npx shadcn@latest add card badge tabs skeleton button separator

# 차트 라이브러리
npm install recharts

# 추가 의존성
npm install lucide-react    # 아이콘
```

### 핵심 패키지 목록

```json
{
  "dependencies": {
    "react": "^19.0.0",
    "react-dom": "^19.0.0",
    "recharts": "^2.12.0",
    "lucide-react": "^0.400.0",
    "tailwind-merge": "^2.0.0",
    "class-variance-authority": "^0.7.0",
    "clsx": "^2.0.0"
  },
  "devDependencies": {
    "vite": "^6.0.0",
    "@vitejs/plugin-react": "^4.0.0",
    "typescript": "^5.5.0",
    "@types/react": "^19.0.0",
    "@types/node": "^20.0.0",
    "tailwindcss": "^4.0.0",
    "@tailwindcss/vite": "^4.0.0",
    "eslint": "^9.0.0"
  }
}
```

---

## 6. Supabase 테이블 생성

Supabase Dashboard → SQL Editor에서 실행하거나, 마이그레이션 파일을 사용합니다.

```bash
# Supabase CLI 설치 (선택)
scoop bucket add supabase https://github.com/supabase/scoop-bucket.git
scoop install supabase
```

테이블 생성 SQL은 `backend/` 하위 마이그레이션 파일로 관리됩니다 (Phase 1에서 작성 예정).

---

## 7. 개발 서버 실행

```bash
# 터미널 1: Backend
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000

# 터미널 2: Frontend (Vite)
cd frontend
npm run dev
# → http://localhost:5173

# 터미널 3: MCP 서버 (필요 시)
cd backend
python -m app.mcp.news_server
```

---

## 8. 유용한 scoop 패키지 (선택)

```bash
# 개발 편의 도구
scoop install lazygit      # Git TUI
scoop install delta        # Git diff 하이라이터
scoop install httpie       # CLI HTTP 클라이언트 (API 테스트용)
```

---

## 9. 체크리스트

개발 시작 전 확인사항:

- [ ] Python 3.12+ 설치됨
- [ ] Node.js 20+ 설치됨
- [ ] EODHD API 키 발급 완료
- [ ] NewsAPI 키 발급 완료
- [ ] Anthropic API 키 발급 완료
- [ ] Supabase 프로젝트 생성 완료
- [ ] `backend/.env` 파일 작성 완료
- [ ] Backend 가상환경 + 의존성 설치 완료
- [ ] Frontend 의존성 설치 완료
- [ ] Playwright MCP + Chromium 브라우저 설치 완료
- [ ] `.mcp.json` MCP 서버 등록 완료
