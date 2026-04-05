import type {
  EconomicIndicator,
  MacroRegime,
  MarketIndex,
  MarketReport,
  NewsArticle,
  NewsArticleEnriched,
  NewsImpactAnalysis,
  RotationSignal,
  Sector,
  SectorScoreboard,
  SectorWithHistory,
} from "@/types";

const BASE_URL = "/api";

async function fetchJson<T>(path: string): Promise<T> {
  const response = await fetch(`${BASE_URL}${path}`);
  if (!response.ok) {
    throw new Error(`API error: ${response.status} ${response.statusText}`);
  }
  return response.json();
}

export const api = {
  getIndices: () => fetchJson<MarketIndex[]>("/market/indices"),
  getSectors: () => fetchJson<Sector[]>("/market/sectors"),
  getIndicators: () => fetchJson<EconomicIndicator[]>("/market/indicators"),
  getRegime: () => fetchJson<MacroRegime>("/market/regime"),

  getNewsArticles: (category?: string, limit = 20) => {
    const params = new URLSearchParams();
    if (category) params.set("category", category);
    params.set("limit", String(limit));
    return fetchJson<NewsArticle[]>(`/news/articles?${params}`);
  },
  getNewsSummaries: (limit = 10) =>
    fetchJson<NewsArticleEnriched[]>(`/news/summaries?limit=${limit}`),
  getNewsImpacts: () => fetchJson<NewsImpactAnalysis[]>("/news/impacts"),

  getReport: () => fetchJson<MarketReport>("/analysis/report"),
  getScoreboards: (batchType?: string) => {
    const params = batchType ? `?batch_type=${batchType}` : "";
    return fetchJson<SectorScoreboard[]>(`/analysis/scoreboards${params}`);
  },
  getSignals: () => fetchJson<RotationSignal[]>("/analysis/signals"),

  getSectorsWithHistory: (days = 30) =>
    fetchJson<SectorWithHistory[]>(`/market/sectors-with-history?days=${days}`),
};
