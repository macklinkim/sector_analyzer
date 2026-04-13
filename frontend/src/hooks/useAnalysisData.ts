import { useCallback, useEffect, useState } from "react";
import { api } from "@/lib/api";
import { getCached, setCache } from "@/lib/utils";
import type { MarketReport, RotationSignal, SectorScoreboard } from "@/types";

const CACHE_KEY = "analysis_data";

interface AnalysisData {
  scoreboards: SectorScoreboard[];
  signals: RotationSignal[];
  report: MarketReport | null;
  loading: boolean;
  error: string | null;
}

interface CachedAnalysisData {
  scoreboards: SectorScoreboard[];
  signals: RotationSignal[];
  report: MarketReport | null;
}

export function useAnalysisData(): AnalysisData & { refresh: () => void } {
  const [data, setData] = useState<AnalysisData>(() => {
    const cached = getCached<CachedAnalysisData>(CACHE_KEY);
    if (cached) {
      return { ...cached, loading: false, error: null };
    }
    return {
      scoreboards: [],
      signals: [],
      report: null,
      loading: true,
      error: null,
    };
  });

  const fetchData = useCallback(async () => {
    setData((prev) => ({ ...prev, loading: true, error: null }));
    try {
      const [scoreboards, signals, report] = await Promise.all([
        api.getScoreboards(),
        api.getSignals(),
        api.getReport().catch(() => null),
      ]);
      setCache(CACHE_KEY, { scoreboards, signals, report });
      setData({ scoreboards, signals, report, loading: false, error: null });
    } catch (err) {
      setData((prev) => ({
        ...prev,
        loading: false,
        error: err instanceof Error ? err.message : "Failed to fetch analysis",
      }));
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return { ...data, refresh: fetchData };
}
