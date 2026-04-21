import { useMemo } from "react";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useCryptoData } from "@/hooks/useCryptoData";
import { useCryptoTicker, type CryptoTicker } from "@/hooks/useCryptoTicker";
import { cn } from "@/lib/utils";
import type { CoinAiScore, CoinMetadata, CoinNews } from "@/types";

function formatPrice(price: number | undefined): string {
  if (price === undefined || !Number.isFinite(price)) return "-";
  if (price >= 1000) return price.toLocaleString("en-US", { maximumFractionDigits: 0 });
  if (price >= 1) return price.toFixed(2);
  return price.toFixed(4);
}

function formatVolume(vol: number | undefined): string {
  if (vol === undefined || !Number.isFinite(vol) || vol === 0) return "-";
  if (vol >= 1e9) return `${(vol / 1e9).toFixed(1)}B`;
  if (vol >= 1e6) return `${(vol / 1e6).toFixed(1)}M`;
  if (vol >= 1e3) return `${(vol / 1e3).toFixed(1)}K`;
  return vol.toFixed(0);
}

function changeColor(change: number | undefined): string {
  if (change === undefined || !Number.isFinite(change)) return "text-muted-foreground";
  if (change > 0) return "text-bullish";
  if (change < 0) return "text-bearish";
  return "text-muted-foreground";
}

function recBadgeVariant(rec: string): "bullish" | "bearish" | "default" {
  if (rec === "overweight") return "bullish";
  if (rec === "underweight") return "bearish";
  return "default";
}

function recLabel(rec: string): string {
  if (rec === "overweight") return "비중확대";
  if (rec === "underweight") return "비중축소";
  return "중립";
}

export function CryptoTab() {
  const { coins, news, scores, loading } = useCryptoData();

  const symbols = useMemo(() => coins.map((c) => c.symbol), [coins]);
  const tickers = useCryptoTicker(symbols);

  const majorCoins = coins.filter((c) => !c.is_ai);
  const aiCoins = coins.filter((c) => c.is_ai);

  return (
    <div
      id="panel-crypto"
      role="tabpanel"
      aria-labelledby="tab-crypto"
      className="space-y-3 p-2 sm:space-y-4 sm:p-4"
    >
      <BtcEthStrip coins={coins} tickers={tickers} loading={loading} />

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <CoinTable title="대형" coins={majorCoins} tickers={tickers} loading={loading} />
        <CoinTable title="AI 섹터" coins={aiCoins} tickers={tickers} loading={loading} />
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <AiScoreTable scores={scores} coins={coins} loading={loading} />
        <CryptoNewsFeed news={news} loading={loading} />
      </div>
    </div>
  );
}

function BtcEthStrip({
  coins,
  tickers,
  loading,
}: {
  coins: CoinMetadata[];
  tickers: Record<string, CryptoTicker>;
  loading: boolean;
}) {
  const featured = coins.filter((c) => ["btc", "eth"].includes(c.symbol));
  if (loading && featured.length === 0) {
    return <Skeleton className="h-16 w-full" />;
  }
  return (
    <div className="grid grid-cols-2 gap-3">
      {featured.map((c) => {
        const t = tickers[c.symbol];
        return (
          <div
            key={c.coin_id}
            className="flex items-center justify-between gap-3 rounded-lg border border-border bg-card px-4 py-3"
          >
            <div className="flex items-center gap-2">
              {c.image_url && (
                <img src={c.image_url} alt={c.symbol} className="h-7 w-7 rounded-full" />
              )}
              <div>
                <p className="text-sm font-semibold text-foreground">{c.symbol.toUpperCase()}</p>
                <p className="text-[10px] text-muted-foreground">{c.name}</p>
              </div>
            </div>
            <div className="text-right">
              <p className="font-mono text-base font-bold tabular-nums text-foreground">
                ${formatPrice(t?.price)}
              </p>
              <p className={cn("font-mono text-xs tabular-nums", changeColor(t?.change24h))}>
                {t?.change24h !== undefined
                  ? `${t.change24h >= 0 ? "+" : ""}${t.change24h.toFixed(2)}%`
                  : "—"}
              </p>
            </div>
          </div>
        );
      })}
    </div>
  );
}

function CoinTable({
  title,
  coins,
  tickers,
  loading,
}: {
  title: string;
  coins: CoinMetadata[];
  tickers: Record<string, CryptoTicker>;
  loading: boolean;
}) {
  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-sm">{title}</CardTitle>
      </CardHeader>
      <CardContent className="overflow-x-auto">
        {loading && coins.length === 0 ? (
          <Skeleton className="h-40 w-full" />
        ) : coins.length === 0 ? (
          <p className="py-4 text-center text-xs text-muted-foreground">데이터 없음</p>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border text-xs text-muted-foreground">
                <th className="px-2 py-2 text-left">코인</th>
                <th className="px-2 py-2 text-right">가격 (USDT)</th>
                <th className="px-2 py-2 text-right">24h</th>
                <th className="px-2 py-2 text-right">거래량</th>
              </tr>
            </thead>
            <tbody>
              {coins.map((c) => {
                const t = tickers[c.symbol];
                return (
                  <tr key={c.coin_id} className="border-b border-border/30">
                    <td className="px-2 py-2">
                      <div className="flex items-center gap-2">
                        {c.image_url && (
                          <img
                            src={c.image_url}
                            alt={c.symbol}
                            className="h-5 w-5 rounded-full"
                          />
                        )}
                        <span className="font-mono text-xs font-semibold">
                          {c.symbol.toUpperCase()}
                        </span>
                      </div>
                    </td>
                    <td className="px-2 py-2 text-right font-mono tabular-nums">
                      ${formatPrice(t?.price)}
                    </td>
                    <td
                      className={cn(
                        "px-2 py-2 text-right font-mono text-xs tabular-nums",
                        changeColor(t?.change24h),
                      )}
                    >
                      {t?.change24h !== undefined
                        ? `${t.change24h >= 0 ? "+" : ""}${t.change24h.toFixed(2)}%`
                        : "—"}
                    </td>
                    <td className="px-2 py-2 text-right font-mono text-xs text-muted-foreground tabular-nums">
                      {formatVolume(t?.volume24h)}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </CardContent>
    </Card>
  );
}

function AiScoreTable({
  scores,
  coins,
  loading,
}: {
  scores: CoinAiScore[];
  coins: CoinMetadata[];
  loading: boolean;
}) {
  const coinMap = new Map(coins.map((c) => [c.coin_id, c]));
  const sorted = [...scores].sort((a, b) => b.ai_score - a.ai_score);

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-sm">AI Score (1일 1회)</CardTitle>
      </CardHeader>
      <CardContent className="overflow-x-auto">
        {loading && scores.length === 0 ? (
          <Skeleton className="h-40 w-full" />
        ) : scores.length === 0 ? (
          <p className="py-4 text-center text-xs text-muted-foreground">
            아직 AI 분석 결과가 없습니다
          </p>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border text-xs text-muted-foreground">
                <th className="px-2 py-2 text-left">코인</th>
                <th className="px-2 py-2 text-right">AI Score</th>
                <th className="px-2 py-2 text-center">Signal</th>
              </tr>
            </thead>
            <tbody>
              {sorted.map((s) => {
                const c = coinMap.get(s.coin_id);
                return (
                  <tr key={s.id} className="border-b border-border/30">
                    <td className="px-2 py-2">
                      <div className="flex items-center gap-2">
                        {c?.image_url && (
                          <img
                            src={c.image_url}
                            alt={c.coin_id}
                            className="h-5 w-5 rounded-full"
                          />
                        )}
                        <span className="font-mono text-xs font-semibold">
                          {(c?.symbol ?? s.coin_id).toUpperCase()}
                        </span>
                      </div>
                      {s.reasoning && (
                        <p className="mt-0.5 line-clamp-2 text-[10px] text-muted-foreground">
                          {s.reasoning}
                        </p>
                      )}
                    </td>
                    <td
                      className={cn(
                        "px-2 py-2 text-right font-mono font-bold tabular-nums",
                        changeColor(s.ai_score),
                      )}
                    >
                      {s.ai_score.toFixed(2)}
                    </td>
                    <td className="px-2 py-2 text-center">
                      <Badge variant={recBadgeVariant(s.recommendation)}>
                        {recLabel(s.recommendation)}
                      </Badge>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </CardContent>
    </Card>
  );
}

function CryptoNewsFeed({ news, loading }: { news: CoinNews[]; loading: boolean }) {
  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-sm">뉴스 (RSS 통합)</CardTitle>
      </CardHeader>
      <CardContent>
        {loading && news.length === 0 ? (
          <Skeleton className="h-40 w-full" />
        ) : news.length === 0 ? (
          <p className="py-4 text-center text-xs text-muted-foreground">뉴스 없음</p>
        ) : (
          <ul className="space-y-2">
            {news.slice(0, 15).map((n) => {
              const sentimentColor =
                n.sentiment === "positive"
                  ? "text-bullish"
                  : n.sentiment === "negative"
                    ? "text-bearish"
                    : "text-muted-foreground";
              return (
                <li key={n.url} className="border-b border-border/30 pb-2 last:border-b-0">
                  <a
                    href={n.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="block text-sm text-foreground hover:underline"
                  >
                    {n.title}
                  </a>
                  <div className="mt-0.5 flex items-center gap-2 text-[10px] text-muted-foreground">
                    <span>{n.source ?? "—"}</span>
                    <span>{new Date(n.published_at).toLocaleString("ko-KR")}</span>
                    <span className={sentimentColor}>{n.sentiment ?? "neutral"}</span>
                    {n.related_coins && n.related_coins.length > 0 && (
                      <span className="truncate font-mono">
                        {n.related_coins.map((c) => c.toUpperCase()).join(" · ")}
                      </span>
                    )}
                  </div>
                </li>
              );
            })}
          </ul>
        )}
      </CardContent>
    </Card>
  );
}
