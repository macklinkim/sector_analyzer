#!/usr/bin/env bash
# ----------------------------------------------------------------
# 분할 트리거 스크립트
# Usage: ./trigger-split.sh [base_url] [api_key]
#
# 1) /health       — Render wake-up
# 2) /trigger/data + /trigger/news — 병렬 실행
# 3) data+news 완료 대기
# 4) /trigger/analyze — AI 분석
# ----------------------------------------------------------------

set -euo pipefail

BASE_URL="${1:-https://sector-analyzer.onrender.com}"
API_KEY="${2:-economi-trigger-2026}"
API_BASE="$BASE_URL/api/analysis"

log() { echo "[$(date '+%H:%M:%S')] $1"; }

# --- Step 1: Wake-up ---
log "Step 1/4: Waking up server..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" --max-time 90 "$BASE_URL/health")
if [ "$HTTP_CODE" != "200" ]; then
  log "WARN: health check returned $HTTP_CODE, retrying in 10s..."
  sleep 10
  curl -s -o /dev/null --max-time 90 "$BASE_URL/health"
fi
log "Server is awake."

# --- Step 2: Data + News 병렬 ---
log "Step 2/4: Triggering data + news in parallel..."

DATA_OUT=$(mktemp)
NEWS_OUT=$(mktemp)
trap 'rm -f "$DATA_OUT" "$NEWS_OUT"' EXIT

curl -s --max-time 180 \
  -X POST "$API_BASE/trigger/data" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -o "$DATA_OUT" -w "\n%{http_code}" &
PID_DATA=$!

curl -s --max-time 180 \
  -X POST "$API_BASE/trigger/news" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -o "$NEWS_OUT" -w "\n%{http_code}" &
PID_NEWS=$!

# 병렬 완료 대기
DATA_OK=0
NEWS_OK=0

wait $PID_DATA && DATA_OK=1 || true
wait $PID_NEWS && NEWS_OK=1 || true

DATA_HTTP=$(tail -1 "$DATA_OUT" 2>/dev/null || echo "000")
NEWS_HTTP=$(tail -1 "$NEWS_OUT" 2>/dev/null || echo "000")

log "Step 3/4: Results — data=$DATA_HTTP, news=$NEWS_HTTP"

if [ "$DATA_HTTP" != "200" ] && [ "$NEWS_HTTP" != "200" ]; then
  log "ERROR: Both data and news failed. Skipping analyze."
  cat "$DATA_OUT" 2>/dev/null; echo
  cat "$NEWS_OUT" 2>/dev/null; echo
  exit 1
fi

[ "$DATA_HTTP" != "200" ] && log "WARN: data trigger failed ($DATA_HTTP), continuing with news only"
[ "$NEWS_HTTP" != "200" ] && log "WARN: news trigger failed ($NEWS_HTTP), continuing with data only"

# --- Step 3: Analyze ---
log "Step 4/4: Triggering AI analysis..."
ANALYZE_RESP=$(curl -s --max-time 300 \
  -X POST "$API_BASE/trigger/analyze" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -w "\nHTTP:%{http_code}")

ANALYZE_HTTP=$(echo "$ANALYZE_RESP" | grep "^HTTP:" | cut -d: -f2)
ANALYZE_BODY=$(echo "$ANALYZE_RESP" | grep -v "^HTTP:")

if [ "$ANALYZE_HTTP" = "200" ]; then
  log "SUCCESS: All stages completed."
  echo "$ANALYZE_BODY"
else
  log "ERROR: Analyze failed (HTTP $ANALYZE_HTTP)"
  echo "$ANALYZE_BODY"
  exit 1
fi
