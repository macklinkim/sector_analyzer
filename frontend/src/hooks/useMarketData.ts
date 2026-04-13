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
  lastUpdated: string;
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
      const lastUpdated = new Date().toISOString();
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
