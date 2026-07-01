/**
 * Cloudflare Cron Trigger Worker — 데이터 파이프라인 스케줄러.
 *
 * 기존 GitHub Actions cron이 60일 무커밋 시 자동 비활성화되던 문제를 대체.
 * Cloudflare cron은 자동 비활성화가 없고, 백엔드 트리거가 즉시 202를 반환하므로
 * 짧은 응답 타임아웃 문제(cron-job.org 실패 원인)도 발생하지 않음.
 *
 * TRIGGER_API_KEY는 코드에 두지 말고 Worker secret으로 주입:
 *   npx wrangler secret put TRIGGER_API_KEY
 */

const RAILWAY = "https://economy-analyzer-production.up.railway.app";

// wrangler.jsonc의 crypto 스케줄과 동일해야 함.
const CRYPTO_CRON = "0 4 * * *";

export default {
  async scheduled(event, env, ctx) {
    const key = env.TRIGGER_API_KEY;
    if (!key) {
      console.error("TRIGGER_API_KEY secret not set — skipping");
      return;
    }

    if (event.cron === CRYPTO_CRON) {
      await ping(`${RAILWAY}/api/crypto/trigger/daily`, { "X-Trigger-Key": key });
    } else {
      await ping(`${RAILWAY}/api/analysis/trigger/all`, { "X-API-Key": key });
    }
  },
};

async function ping(url, headers) {
  try {
    const res = await fetch(url, { method: "POST", headers });
    const body = await res.text();
    console.log(`POST ${url} -> ${res.status} ${body.slice(0, 200)}`);
  } catch (err) {
    console.error(`POST ${url} failed: ${err}`);
  }
}
