# Fly.io 배포 런북

Dockerfile + fly.toml(레포 루트) 사용. 단일 always-on 머신 = APScheduler + fire-and-forget 배치 유지.

## 1. flyctl 설치 (Windows / scoop)

```powershell
scoop install flyctl
# 또는: iwr https://fly.io/install.ps1 -useb | iex
```

## 2. 가입 / 로그인

```powershell
fly auth signup   # 최초 (카드 등록). 이미 있으면 fly auth login
```

## 3. 앱 생성

`fly.toml`의 `app = "economi-analyzer"` 이름이 전역에서 중복이면 실패 → 유니크하게 바꿔라
(예: `economi-analyzer-mack`). 바꾼 뒤:

```powershell
fly apps create economi-analyzer-mack
```

## 4. 시크릿 등록 (KeysValues 파일 값)

```powershell
fly secrets set `
  ANTHROPIC_API_KEY=... `
  EODHD_API_KEY=dummy `
  NEWSAPI_KEY=... `
  SUPABASE_URL=... `
  SUPABASE_SERVICE_KEY=... `
  SUPABASE_JWT_SECRET=... `
  TRIGGER_API_KEY=... `
  CORS_ORIGINS=https://sectoranalyzerfrontend2026.kopserf.workers.dev
```
- `EODHD_API_KEY`는 config 필수 필드라 안 쓰더라도 아무 값 필요.
- 시크릿은 fly.toml `[env]` 아님 — 위 명령으로 암호화 저장됨.

## 5. 배포

```powershell
fly deploy --ha=false
```
빌드(x86) → 이미지 푸시 → 머신 기동. `/health` 통과하면 완료.
`--ha=false` 필수 — 안 붙이면 Fly가 HA로 머신 2개 띄워 APScheduler 배치가 중복 실행됨.
실수로 2개 되면: `fly scale count 1 --yes`.

## 6. 확인

```powershell
fly status
fly logs
curl https://economi-analyzer-mack.fly.dev/health
```

## 7. 프론트 / 트리거 URL 교체

- 프론트엔드 API base URL을 `https://<app>.fly.dev`로 변경 후 Cloudflare Workers 재배포.
- Cloudflare Cron Worker 트리거 대상 호스트를 새 도메인으로 교체
  (`/api/analysis/trigger/*`, `/api/crypto/trigger/*`, 헤더 `X-Trigger-Key`).

## 갱신(재배포)

```powershell
fly deploy --ha=false   # 코드 변경 후 다시 (--ha=false 꼭)
```

## 주의

- `auto_stop_machines = false` / `min_machines_running = 1` 반드시 유지 — 꺼지면 스케줄러·백그라운드 배치 죽음.
- 512mb에서 배치 OOM 나면 fly.toml `memory = "1024mb"` 후 재배포.
- 비용: 머신 24/7이라 무료 크레딧 초과분 소액 과금 가능. `fly dashboard`에서 사용량 확인.
