# Oracle Cloud Always Free — 백엔드 배포 런북

Railway trial 소진 대체. Oracle Ampere A1(ARM) 영구 무료 VM에 FastAPI 백엔드를 상시 구동한다.
in-process APScheduler가 살아있으므로 배치 스케줄러도 이 VM에서 직접 돈다(Cloudflare Cron 트리거는 백업/수동용으로 유지 가능).

## 1. VM 생성 (Oracle Console)

- Shape: **VM.Standard.A1.Flex** (Ampere ARM) — Always Free. 예: 2 OCPU / 12GB.
- Image: **Ubuntu 24.04** (Python 3.12 기본 탑재, ARM64).
- SSH 키 등록 후 생성. 공인 IP 할당 확인.
- **Security List (VCN → Subnet)**: Ingress 규칙 추가
  - TCP 22 (SSH, 기본 있음)
  - TCP 80, 443 (Caddy TLS)
  - Source 0.0.0.0/0

> Oracle 이미지는 VM 내부 iptables도 막아둔다. `setup.sh`가 80/443을 연다.

## 2. 부트스트랩

```bash
ssh ubuntu@<PUBLIC_IP>
curl -fsSL https://raw.githubusercontent.com/macklinkim/sector_analyzer/master/backend/deploy/setup.sh -o setup.sh
bash setup.sh
```

레포가 private면 `git clone`이 인증을 물음 → PAT 사용하거나 배포 키 등록.

## 3. 환경변수

```bash
nano /opt/economi_analyzer/backend/.env   # KeysValues 파일 값으로 채움
```
필요 키: `ANTHROPIC_API_KEY, EODHD_API_KEY, NEWSAPI_KEY, SUPABASE_URL, SUPABASE_SERVICE_KEY, SUPABASE_JWT_SECRET, TRIGGER_API_KEY, CORS_ORIGINS`.

## 4. 도메인 + HTTPS

프론트가 https(workers.dev)라 백엔드도 https 필수(mixed-content 차단).

1. **DuckDNS**: duckdns.org 로그인 → 서브도메인 생성 → current IP를 Oracle 공인 IP로 설정.
2. Caddyfile 도메인 교체:
   ```bash
   sudo cp /opt/economi_analyzer/backend/deploy/Caddyfile /etc/caddy/Caddyfile
   sudo sed -i 's/YOURNAME.duckdns.org/<yourname>.duckdns.org/' /etc/caddy/Caddyfile
   sudo systemctl restart caddy
   ```
   Caddy가 Let's Encrypt 인증서 자동 발급. `https://<yourname>.duckdns.org/health` 확인.

## 5. 서비스 기동

```bash
sudo systemctl start economi-backend
sudo systemctl status economi-backend
journalctl -u economi-backend -f      # 로그
curl -s http://127.0.0.1:8000/health  # 로컬 헬스체크
```

## 6. 프론트/트리거 URL 교체

- **프론트엔드**: API base URL을 새 `https://<yourname>.duckdns.org`로 변경 후 Cloudflare Workers 재배포.
- **Cloudflare Cron Worker**: 트리거 대상 호스트를 새 도메인으로 교체 (`/api/analysis/trigger/*`, `/api/crypto/trigger/*`, 헤더 `X-Trigger-Key: <TRIGGER_API_KEY>`).
- **CORS**: `.env`의 `CORS_ORIGINS`에 프론트 workers.dev 도메인 포함 확인.

## 갱신(재배포)

```bash
cd /opt/economi_analyzer && git pull --ff-only
/opt/economi_analyzer/.venv/bin/pip install -e backend   # 의존성 변경 시
sudo systemctl restart economi-backend
```

## 트러블슈팅

- ARM 휠 빌드 실패 → `build-essential` 설치됨(setup.sh). 그래도 실패 시 해당 패키지 로그 확인.
- healthcheck 502 → 서비스 미기동/.env 오류. `journalctl -u economi-backend -e`.
- TLS 발급 실패 → 80/443 Oracle Security List + iptables 둘 다 열렸는지, DuckDNS IP 일치 확인.
- 배치 도중 OOM → A1 Flex 메모리 상향(무료 한도 24GB 내).
```
