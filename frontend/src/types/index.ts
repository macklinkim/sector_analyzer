// frontend/src/types/index.ts

// --- Market Types ---

export interface MarketIndex {
  symbol: string;
  name: string;
  price: number;
  change_percent: number;
  collected_at: string;
}

export interface Sector {
  name: string;
  etf_symbol: string;
  price: number;
  change_percent: number;
  volume: number;
  avg_volume_20d: number | null;
  volume_change_percent: number | null;
  relative_strength: number | null;
  momentum_1w: number | null;
  momentum_1m: number | null;
  momentum_3m: number | null;
  momentum_6m: number | null;
  momentum_1y: number | null;
  week_52_low: number | null;
  week_52_high: number | null;
  rs_rank: number | null;
  collected_at: string;
}

export interface EconomicIndicator {
  indicator_name: string;
  value: number;
  previous_value: number | null;
  change_direction: string;
  source: string;
  reported_at: string;
}

// --- News Types ---

export interface NewsArticle {
  category: string;
  title: string;
  source: string;
  url: string;
  summary: string | null;
  published_at: string;
  collected_at: string;
}

export interface NewsArticleEnriched extends NewsArticle {
  summary_ko: string | null;
  impact_label: string | null;
  impact_score: number;
  related_sector: string | null;
}

export interface NewsImpactAnalysis {
  news_url: string;
  sector_name: string;
  impact_score: number;
  impact_direction: string;
  reasoning: string;
  rotation_relevance: number;
  batch_type: string;
  analyzed_at: string;
}

// --- Analysis Types ---

export interface MacroRegime {
  regime: "goldilocks" | "reflation" | "stagflation" | "deflation";
  growth_direction: string;
  inflation_direction: string;
  transition_from: string | null;
  transition_probability: number | null;
  regime_probabilities: Record<string, number>;
  indicators_snapshot: Record<string, unknown> | null;
  reasoning: string;
  batch_type: string;
  analyzed_at: string;
}

export interface SectorScoreboard {
  sector_name: string;
  etf_symbol: string;
  base_score: number;
  override_score: number;
  news_sentiment_score: number;
  momentum_score: number;
  final_score: number;
  rank: number;
  recommendation: "overweight" | "neutral" | "underweight";
  reasoning: string;
  batch_type: string;
  scored_at: string;
}

export interface RotationSignal {
  signal_type: string;
  from_sector: string | null;
  to_sector: string | null;
  strength: number;
  base_score: number | null;
  override_adjustment: number | null;
  final_score: number;
  reasoning: string;
  supporting_news_urls: string[];
  batch_type: string;
  detected_at: string;
}

export interface MarketReport {
  batch_type: string;
  summary: string;
  key_highlights: string[];
  regime: MacroRegime;
  top_sectors: SectorScoreboard[];
  bottom_sectors: SectorScoreboard[];
  rotation_signals: RotationSignal[];
  report_date: string;
  analyzed_at: string;
  disclaimer: string;
}

// --- Sparkline Types ---

export interface SparkPoint {
  date: string;
  close: number;
}

export interface SectorWithHistory {
  sector: string;
  name: string;
  change_percent: number;
  price: number;
  history: SparkPoint[];
}

// --- Regime Helpers ---

export type RegimeType = MacroRegime["regime"];

export const REGIME_COLORS: Record<RegimeType, string> = {
  goldilocks: "var(--color-goldilocks)",
  reflation: "var(--color-reflation)",
  stagflation: "var(--color-stagflation)",
  deflation: "var(--color-deflation)",
};

export const REGIME_LABELS: Record<RegimeType, string> = {
  goldilocks: "Goldilocks",
  reflation: "Reflation",
  stagflation: "Stagflation",
  deflation: "Deflation",
};
