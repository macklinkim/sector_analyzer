# Railway 마이그레이션 계획

> **작성일:** 2026-04-13
> **목적:** Backend를 Render Free → Railway로 이전하여 spin-down 문제 해결
> **상태:** 계획 수립 완료, 실행 대기

---

## 1. 현재 아키텍처

```
[Cloudflare Workers]  ←→  [Render Free]  ←→  [Supabase]
  프론트엔드 SPA           FastAPI Backend      PostgreSQL DB
  정적 배포                Docker 배포           ap-northeast-1
```

### 현재 문제점
- **Render Free tier**: 15분 무활동 시 spin-down → APScheduler 작동 불가
- **임시 우회**: cron-job.org → `/api/analysis/trigger/all` 외부 트리거
- **APScheduler 중복 실행 위험**: 서버가 깨어있을 때 APScheduler + cron-job.org 동시 실행 가능 → NewsAPI 100 req/일 한도 초과 위험
- **`backend/app/scheduler/jobs.py`**: 현재 비활성화 필요 (아직 미처리)

---

## 2. 마이그레이션 대상

| 구성 | 변경 여부 | 설명 |
|------|:---:|------|
| **Backend (Render → Railway)** | ✅ | 이번 작업 대상 |
| Frontend (Cloudflare Workers) | ❌ | 변경 없음 |
| DB (Supabase) | ❌ | 변경 없음 |
| 프론트 전용 레포 (sector-analyzer-frontend) | ❌ | 변경 없음 |

---

## 3. Railway 이전 시 결정 사항

### 3-1. 스케줄러 전략 (핵심 결정)

Railway Hobby($5/mo)는 **상시 가동**이므로 두 가지 선택지:

| 방안 | 설명 | 장점 | 단점 |
|------|------|------|------|
| **A. APScheduler 복원** | `jobs.py` 그대로 사용, cron-job.org 제거 | 외부 의존 0, 코드 내 스케줄 관리 | 멀티 워커 시 중복 실행 위험 (workers=1 강제) |
| **B. cron-job.org 유지** | APScheduler 비활성화, 외부 트리거만 사용 | Railway 장애 시에도 트리거 기록 남음 | 외부 서비스 의존 |
| **C. Railway Cron Job** | Railway 네이티브 cron 사용 | 플랫폼 통합, 별도 설정 불필요 | Railway cron은 별도 서비스로 과금 |

**추천: A안** — Railway는 spin-down 없으므로 APScheduler가 정상 작동. 가장 단순.

### 3-2. 환경변수

Render에서 Railway로 옮겨야 할 환경변수:

```
ANTHROPIC_API_KEY
EODHD_API_KEY
NEWSAPI_KEY
SUPABASE_URL
SUPABASE_SERVICE_KEY
TRIGGER_API_KEY=economi-trigger-2026
ALLOWED_USERS
CORS_ORIGINS=https://sectoranalyzerfrontend2026.kopserf.workers.dev
```

### 3-3. Docker 설정

현재 `Dockerfile`은 Railway에서 **그대로 사용 가능**:
- Python 3.12-slim
- tzdata 설치 (US/Eastern 타임존)
- 단일 워커 (`--workers 1`)
- 포트 8000

Railway는 `PORT` 환경변수를 자동 주입하므로 Dockerfile CMD에서 `$PORT` 사용 권장.

### 3-4. CORS 업데이트

Railway 배포 후 새 URL이 생기면:
1. Cloudflare 프론트엔드의 `VITE_API_URL` 변경 필요
2. 또는 Railway에서 커스텀 도메인 설정

---

## 4. 실행 체크리스트

### Phase 1: Railway 셋업
- [ ] Railway 계정 생성 / Hobby 플랜 ($5/mo)
- [ ] `railway login` CLI 설치 및 인증
- [ ] `railway init` 프로젝트 생성
- [ ] 환경변수 설정 (위 목록 전부)
- [ ] `railway up` 또는 GitHub 연동 배포

### Phase 2: 스케줄러 정리
- [ ] `backend/app/scheduler/jobs.py` — A안 선택 시 그대로, B안 선택 시 비활성화
- [ ] `backend/app/main.py` lifespan — 스케줄러 전략에 따라 수정
- [ ] 중복 실행 방지 확인

### Phase 3: 프론트엔드 연결
- [ ] Railway 배포 URL 확인
- [ ] Cloudflare 프론트엔드 `VITE_API_URL` 업데이트
- [ ] `npm run build && npx wrangler deploy`
- [ ] CORS 설정 확인

### Phase 4: 검증
- [ ] `GET /health` 정상 응답
- [ ] `POST /api/analysis/trigger/all` 수동 실행 → DB 갱신 확인
- [ ] APScheduler 로그 확인 (A안 선택 시)
- [ ] 프론트엔드에서 데이터 정상 표시

### Phase 5: Render 정리
- [ ] Render 서비스 중지/삭제
- [ ] cron-job.org job 삭제 (A안 선택 시) 또는 URL 변경 (B안 선택 시)
- [ ] README.md 배포 URL 업데이트

---

## 5. 롤백 계획

Railway 문제 발생 시:
1. Render 서비스 재시작 (삭제 전까지 유효)
2. 프론트엔드 `VITE_API_URL`을 Render URL로 복원
3. cron-job.org URL을 Render로 복원

---

## 6. 참고 파일

| 파일 | 역할 |
|------|------|
| `Dockerfile` | 컨테이너 빌드 (Railway에서 그대로 사용) |
| `render.yaml` | Render 설정 (마이그레이션 후 삭제 가능) |
| `backend/app/main.py` | FastAPI + lifespan 스케줄러 |
| `backend/app/scheduler/jobs.py` | APScheduler cron 정의 |
| `backend/app/api/routes/analysis.py` | 트리거 엔드포인트 (trigger/all 포함) |
| `scripts/trigger-split.sh` | 수동 트리거 스크립트 |
| `TRIGGER_API_KEY` | 트리거 인증 키: `economi-trigger-2026` |

---

## 7. 미처리 사항 (이번 세션에서 보류)

1. **APScheduler 비활성화**: `main.py` lifespan에서 스케줄러 시작 코드 주석/제거 — Railway 전략 확정 후 처리
2. **Qdrant MCP 서버**: 사용자 판단으로 보류
