# Backend Rules

## Python Conventions
- Python 3.12+ 필수, type hints 모든 함수에 적용
- async/await 패턴 사용 (FastAPI 비동기)
- pydantic v2 BaseModel for request/response schemas
- pydantic-settings for environment variable management
- Import 순서: stdlib → third-party → local (isort 규칙)

## FastAPI
- 라우터는 `app/api/routes/` 하위에 도메인별 분리
- 의존성 주입은 `app/api/deps.py`에 정의
- 에러 응답은 HTTPException으로 통일

## LangGraph Agents
- 각 에이전트는 `app/agents/` 하위 독립 모듈
- 공유 상태는 `app/agents/state.py`의 TypedDict로 정의
- 에이전트 간 데이터 전달은 반드시 State를 통해서만
- 외부 API 호출은 `app/services/` 클라이언트를 통해서만

## Supabase
- 테이블 조작은 `app/services/supabase.py` 클라이언트를 통해서만
- Raw SQL 금지, Supabase Python SDK 사용

## Playwright MCP (Heavy Track)
- API로 얻을 수 있는 데이터는 절대 Playwright 사용 금지 → Fast Track(API) 사용
- Playwright는 API 미제공 동적 SPA 데이터 수집에만 사용
- 브라우저 인스턴스 동시 실행 제한 (최대 2개)
- 타임아웃 30초 강제, 초과 시 해당 태스크 건너뛰기
- Anti-bot 차단 시 graceful fallback: 에러 로그 + API 데이터만으로 분석 계속
- 스크린샷 → Claude Vision 분석 연동 시 이미지 크기 최적화 (max 1280px 너비)
- Playwright 태스크 정의는 `app/mcp/playwright_tasks.py`에 집중 관리

## Testing
- pytest + pytest-asyncio
- 외부 API는 mock 처리
- 에이전트 테스트: 각 노드를 독립적으로 테스트
- Playwright 테스트: 실제 브라우저 대신 mock response 사용
