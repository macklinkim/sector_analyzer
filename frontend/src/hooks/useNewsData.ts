import { useCallback, useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { NewsArticle, NewsImpactAnalysis } from "@/types";

interface NewsData {
  articles: NewsArticle[];
  impacts: NewsImpactAnalysis[];
  loading: boolean;
  error: string | null;
}

export function useNewsData(category?: string): NewsData & { refresh: () => void } {
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
        api.getNewsArticles(category),
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
  }, [category]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return { ...data, refresh: fetchData };
}
