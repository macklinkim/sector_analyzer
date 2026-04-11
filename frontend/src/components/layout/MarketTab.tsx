import { SectorComparisonCharts } from "@/components/chart/SectorComparisonCharts";
import { EconomicCalendar } from "@/components/news/EconomicCalendar";
import { NewsImpactFeed } from "@/components/news/NewsImpactFeed";
import { MarketMovers } from "@/components/sector/MarketMovers";
import { SectorHeatmap } from "@/components/sector/SectorHeatmap";
import { SectorSparkline } from "@/components/sector/SectorSparkline";
import { SectorStockTreemap } from "@/components/sector/SectorStockTreemap";
import type { MarketDataState, NewsDataState } from "@/types";

interface MarketTabProps {
  marketData: MarketDataState;
  newsData: NewsDataState;
  selectedSector: string | null;
  setSelectedSector: (sector: string | null) => void;
}

export function MarketTab({
  marketData,
  newsData,
  selectedSector,
  setSelectedSector,
}: MarketTabProps) {
  const selectedEtf =
    marketData.sectors.find((s) => s.name === selectedSector)?.etf_symbol ??
    null;

  return (
    <div
      id="panel-market"
      role="tabpanel"
      aria-labelledby="tab-market"
      className="space-y-4 p-4"
    >
      {/* Row 1: SectorHeatmap (풀폭) */}
      <SectorHeatmap
        sectors={marketData.sectors}
        loading={marketData.loading}
        onSectorClick={setSelectedSector}
      />

      {/* Row 2: SectorStockTreemap — 풀폭 (요구사항) */}
      <SectorStockTreemap
        selectedSector={selectedSector}
        etfSymbol={selectedEtf}
      />

      {/* Row 3: Sparkline + MarketMovers (2열) */}
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <SectorSparkline
          sectors={marketData.sectors}
          selectedSector={selectedSector}
          onSectorClick={setSelectedSector}
        />
        <MarketMovers
          sectors={marketData.sectors}
          selectedSector={selectedSector}
        />
      </div>

      {/* Row 4: News + Calendar (2열) */}
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <NewsImpactFeed
          articles={newsData.articles}
          impacts={newsData.impacts}
          crises={newsData.crises}
          loading={newsData.loading}
        />
        <EconomicCalendar
          indicators={marketData.indicators}
          loading={marketData.loading}
        />
      </div>

      {/* Row 5~7: 섹터 비교 차트 스택 (RS, MB, RC) */}
      <SectorComparisonCharts
        sectors={marketData.sectors}
        loading={marketData.loading}
      />
    </div>
  );
}
