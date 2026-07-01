# sector-analyzer-cron

데이터 파이프라인을 스케줄대로 트리거하는 Cloudflare Cron Worker.

## 왜 이걸로 옮겼나

- **GitHub Actions**: 레포에 60일간 커밋이 없으면 스케줄 워크플로우가 자동 비활성화됨 (`disabled_inactivity`) → 2026-06-22 이후 파이프라인 중단의 원인.
- **cron-job.org**: 무료 티어 응답 타임아웃(~30s)에 걸려 3~4분짜리 동기 트리거가 실패.
- **Cloudflare Cron**: 자동 비활성화 없음. 백엔드 트리거를 즉시 202 반환(fire-and-forget)으로 바꿔 타임아웃 문제도 제거.

## 스케줄 (UTC, 기존 GitHub Actions와 동일)

| Cron (UTC)      | ET (EDT)   | 대상 엔드포인트                    |
| --------------- | ---------- | ---------------------------------- |
| `30 8 * * 1-5`  | 04:30 pre  | `POST /api/analysis/trigger/all`   |
| `30 14 * * 1-5` | 10:30 open | `POST /api/analysis/trigger/all`   |
| `0 21 * * 1-5`  | 17:00 post | `POST /api/analysis/trigger/all`   |
| `0 4 * * *`     | 00:00      | `POST /api/crypto/trigger/daily`   |

주말/NYSE 공휴일은 서버의 `is_market_open_today()`가 idempotent하게 스킵한다.

## 배포

```bash
cd cron-worker
npm install
npx wrangler login                       # 최초 1회
npx wrangler secret put TRIGGER_API_KEY   # 프롬프트에 TRIGGER_API_KEY 값 입력 (레포 루트 KeysValues 참조)
npm run deploy
```

## 확인

```bash
npm run tail        # 실시간 로그 (cron 발동 시 POST ... -> 202 확인)
```

수동 테스트(로컬 dev에서 스케줄 강제 발동):

```bash
npm run dev
# 다른 터미널에서:
curl "http://localhost:8787/__scheduled?cron=30+8+*+*+1-5"
```
