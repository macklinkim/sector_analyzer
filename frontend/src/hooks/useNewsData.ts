import { useCallback, useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { NewsArticleEnriched, NewsImpactAnalysis } from "@/types";

interface NewsData {
  articles: NewsArticleEnriched[];
  impacts: NewsImpactAnalysis[];
  loading: boolean;
  error: string | null;
}

export function useNewsData(): NewsData & { refresh: () => void } {
  const [data, setData] = useState<NewsData>({
    articles: [],
    impacts: [],
    loading: true,
    error: null,
  });

  const fetchData = useCallback(async () => {
    setData((prev) => ({ ...prev, loading: true, error: null }));
    try {
      const [articles, impacts] = await Promise.all([
        api.getNewsSummaries(15),
        api.getNewsImpacts(),
      ]);
      setData({ articles, impacts, loading: false, error: null });
    } catch (err) {
      setData((prev) => ({
        ...prev,
        loading: false,
        error: err instanceof Error ? err.message : "Failed to fetch news",
      }));
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return { ...data, refresh: fetchData };
}
