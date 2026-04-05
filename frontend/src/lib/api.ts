import type {
  EconomicIndicator,
  MacroRegime,
  MarketIndex,
  MarketReport,
  NewsArticle,
  NewsImpactAnalysis,
  RotationSignal,
  Sector,
  SectorScoreboard,
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
  getNewsImpacts: () => fetchJson<NewsImpactAnalysis[]>("/news/impacts"),

  getReport: () => fetchJson<MarketReport>("/analysis/report"),
  getScoreboards: (batchType = "pre_market") =>
    fetchJson<SectorScoreboard[]>(`/analysis/scoreboards?batch_type=${batchType}`),
  getSignals: () => fetchJson<RotationSignal[]>("/analysis/signals"),
};
