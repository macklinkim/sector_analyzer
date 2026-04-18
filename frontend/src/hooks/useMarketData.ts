import { useCallback, useEffect, useState } from "react";
import { api } from "@/lib/api";
import { getCached, setCache } from "@/lib/utils";
import type { EconomicIndicator, MacroRegime, MarketIndex, Sector } from "@/types";

const CACHE_KEY = "market_data";

interface MarketData {
  indices: MarketIndex[];
  sectors: Sector[];
  indicators: EconomicIndicator[];
  regime: MacroRegime | null;
  loading: boolean;
  error: string | null;
  lastUpdated: string | null;
}

interface CachedMarketData {
  indices: MarketIndex[];
  sectors: Sector[];
  indicators: EconomicIndicator[];
  regime: MacroRegime | null;
  lastUpdated: string | null;
}

export function useMarketData(): MarketData & { refresh: () => void } {
  const [data, setData] = useState<MarketData>(() => {
    const cached = getCached<CachedMarketData>(CACHE_KEY);
    if (cached) {
      return { ...cached, loading: false, error: null };
    }
    return {
      indices: [],
      sectors: [],
      indicators: [],
      regime: null,
      loading: true,
      error: null,
      lastUpdated: null,
    };
  });

  const fetchData = useCallback(async () => {
    setData((prev) => ({ ...prev, loading: true, error: null }));
    try {
      const [indices, sectors, indicators, regime] = await Promise.all([
        api.getIndices(),
        api.getSectors(),
        api.getIndicators(),
        api.getRegime().catch(() => null),
      ]);
      // lastUpdated = analyst stage 완료 시각 (뉴스/시장/AI 분석 모두 끝난 시점).
      // regime은 analyst 단계에서 저장되므로 analyzed_at이 곧 파이프라인 완료 시각.
      const lastUpdated = regime?.analyzed_at ?? null;
      setCache(CACHE_KEY, { indices, sectors, indicators, regime, lastUpdated });
      setData({
        indices,
        sectors,
        indicators,
        regime,
        loading: false,
        error: null,
        lastUpdated,
      });
    } catch (err) {
      setData((prev) => ({
        ...prev,
        loading: false,
        error: err instanceof Error ? err.message : "Failed to fetch data",
      }));
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return { ...data, refresh: fetchData };
}
