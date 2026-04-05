import { useCallback, useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { MarketReport, RotationSignal, SectorScoreboard } from "@/types";

interface AnalysisData {
  scoreboards: SectorScoreboard[];
  signals: RotationSignal[];
  report: MarketReport | null;
  loading: boolean;
  error: string | null;
}

export function useAnalysisData(): AnalysisData & { refresh: () => void } {
  const [data, setData] = useState<AnalysisData>({
    scoreboards: [],
    signals: [],
    report: null,
    loading: true,
    error: null,
  });

  const fetchData = useCallback(async () => {
    setData((prev) => ({ ...prev, loading: true, error: null }));
    try {
      const [scoreboards, signals, report] = await Promise.all([
        api.getScoreboards(),
        api.getSignals(),
        api.getReport().catch(() => null),
      ]);
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
