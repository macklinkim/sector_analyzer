import { getAuthToken } from "@/lib/supabase";
import type {
  AllowedUser,
  EconomicIndicator,
  GlobalCrisis,
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

const BASE_URL = import.meta.env.VITE_API_URL || "/api";

async function fetchJson<T>(path: string, init?: RequestInit): Promise<T> {
  const headers = new Headers(init?.headers);
  const token = await getAuthToken();
  if (token && !headers.has("Authorization")) {
    headers.set("Authorization", `Bearer ${token}`);
  }
  const response = await fetch(`${BASE_URL}${path}`, { ...init, headers });
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

  getGlobalCrises: () => fetchJson<GlobalCrisis[]>("/news/crises"),

  getSectorStocks: (etfSymbol: string) =>
    fetchJson<{ symbol: string; name: string; close: number; change_p: number; volume: number; market_cap: number }[]>(
      `/market/sector-stocks/${etfSymbol}`
    ),

  checkEmail: (email: string) =>
    fetchJson<{ allowed: boolean }>("/auth/check-email", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email }),
    }),

  getMe: () =>
    fetchJson<{
      identity: string;
      source: "legacy" | "supabase";
      is_admin: boolean;
      photo_url: string | null;
    }>("/auth/me"),

  listAllowedUsers: () => fetchJson<AllowedUser[]>("/auth/allowed-users"),

  addAllowedUser: (name: string) =>
    fetchJson<AllowedUser>("/auth/allowed-users", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name }),
    }),

  deleteAllowedUser: async (name: string): Promise<void> => {
    const headers = new Headers();
    const token = await getAuthToken();
    if (token) headers.set("Authorization", `Bearer ${token}`);
    const resp = await fetch(
      `${BASE_URL}/auth/allowed-users/${encodeURIComponent(name)}`,
      { method: "DELETE", headers },
    );
    if (!resp.ok) {
      const err = await resp.json().catch(() => ({}));
      throw new Error(err.detail ?? `삭제 실패 (${resp.status})`);
    }
  },

  uploadAvatar: async (name: string, file: File): Promise<AllowedUser> => {
    const form = new FormData();
    form.append("file", file);
    const headers = new Headers();
    const token = await getAuthToken();
    if (token) headers.set("Authorization", `Bearer ${token}`);
    const resp = await fetch(
      `${BASE_URL}/auth/allowed-users/${encodeURIComponent(name)}/avatar`,
      { method: "POST", headers, body: form },
    );
    if (!resp.ok) {
      const err = await resp.json().catch(() => ({}));
      throw new Error(err.detail ?? `업로드 실패 (${resp.status})`);
    }
    return resp.json();
  },
};
