import { useCallback, useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { EconomicIndicator, MacroRegime, MarketIndex, Sector } from "@/types";

interface MarketData {
  indices: MarketIndex[];
  sectors: Sector[];
  indicators: EconomicIndicator[];
  regime: MacroRegime | null;
  loading: boolean;
  error: string | null;
  lastUpdated: string | null;
}

export function useMarketData(): MarketData & { refresh: () => void } {
  const [data, setData] = useState<MarketData>({
    indices: [],
    sectors: [],
    indicators: [],
    regime: null,
    loading: true,
    error: null,
    lastUpdated: null,
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
      setData({
        indices,
        sectors,
        indicators,
        regime,
        loading: false,
        error: null,
        lastUpdated: new Date().toISOString(),
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
