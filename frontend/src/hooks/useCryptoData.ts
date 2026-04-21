import { useEffect, useState } from "react";

import { api } from "@/lib/api";
import type { CoinAiScore, CoinMetadata, CoinNews } from "@/types";

export interface CryptoDataState {
  coins: CoinMetadata[];
  news: CoinNews[];
  scores: CoinAiScore[];
  loading: boolean;
  error: string | null;
  refresh: () => void;
}

export function useCryptoData(): CryptoDataState {
  const [coins, setCoins] = useState<CoinMetadata[]>([]);
  const [news, setNews] = useState<CoinNews[]>([]);
  const [scores, setScores] = useState<CoinAiScore[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [tick, setTick] = useState(0);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);

    Promise.all([
      api.getCoinMetadata().catch(() => [] as CoinMetadata[]),
      api.getCoinNews(30).catch(() => [] as CoinNews[]),
      api.getCoinAiScores().catch(() => [] as CoinAiScore[]),
    ])
      .then(([m, n, s]) => {
        if (cancelled) return;
        setCoins(m);
        setNews(n);
        setScores(s);
      })
      .catch((e) => {
        if (!cancelled) setError(e instanceof Error ? e.message : "crypto fetch failed");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [tick]);

  return {
    coins,
    news,
    scores,
    loading,
    error,
    refresh: () => setTick((t) => t + 1),
  };
}
