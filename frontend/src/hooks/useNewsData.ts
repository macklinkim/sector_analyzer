import { useCallback, useEffect, useState } from "react";
import { api } from "@/lib/api";
import { getCached, setCache } from "@/lib/utils";
import type { GlobalCrisis, NewsArticleEnriched, NewsImpactAnalysis } from "@/types";

const CACHE_KEY = "news_data";

interface NewsData {
  articles: NewsArticleEnriched[];
  impacts: NewsImpactAnalysis[];
  crises: GlobalCrisis[];
  loading: boolean;
  error: string | null;
}

interface CachedNewsData {
  articles: NewsArticleEnriched[];
  impacts: NewsImpactAnalysis[];
  crises: GlobalCrisis[];
}

export function useNewsData(): NewsData & { refresh: () => void } {
  const [data, setData] = useState<NewsData>(() => {
    const cached = getCached<CachedNewsData>(CACHE_KEY);
    if (cached) {
      return { ...cached, loading: false, error: null };
    }
    return {
      articles: [],
      impacts: [],
      crises: [],
      loading: true,
      error: null,
    };
  });

  const fetchData = useCallback(async () => {
    setData((prev) => ({ ...prev, loading: true, error: null }));
    try {
      const [articles, impacts, crises] = await Promise.all([
        api.getNewsSummaries(15),
        api.getNewsImpacts(),
        api.getGlobalCrises().catch(() => []),
      ]);
      setCache(CACHE_KEY, { articles, impacts, crises });
      setData({ articles, impacts, crises, loading: false, error: null });
    } catch (err) {
      setData((prev) => ({
        ...prev,
        loading: false,
        error: err instanceof Error ? err.message : "Failed to fetch news",
      }));
    }
  }, []);

  useEffect(() => {
    const cached = getCached<CachedNewsData>(CACHE_KEY);
    if (!cached) {
      fetchData();
    }
  }, [fetchData]);

  return { ...data, refresh: fetchData };
}
