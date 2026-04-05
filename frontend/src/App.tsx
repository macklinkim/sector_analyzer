import { useState } from "react";
import { useMarketData } from "@/hooks/useMarketData";
import { useNewsData } from "@/hooks/useNewsData";
import { GlobalMacroHeader } from "@/components/header/GlobalMacroHeader";
import { SectorHeatmap } from "@/components/sector/SectorHeatmap";
import { SectorSparkline } from "@/components/sector/SectorSparkline";
import { MarketMovers } from "@/components/sector/MarketMovers";
import { NewsImpactFeed } from "@/components/news/NewsImpactFeed";
import { EconomicCalendar } from "@/components/news/EconomicCalendar";

export default function App() {
  const marketData = useMarketData();
  const newsData = useNewsData();
  const [selectedSector, setSelectedSector] = useState<string | null>(null);

  return (
    <div className="min-h-screen bg-background text-foreground">
      {/* Area A: Global Macro Header */}
      <header>
        <GlobalMacroHeader
          indices={marketData.indices}
          indicators={marketData.indicators}
          regime={marketData.regime}
          loading={marketData.loading}
          lastUpdated={marketData.lastUpdated}
        />
      </header>

      {/* Area B + C: Side by side */}
      <main className="grid grid-cols-1 gap-4 p-4 lg:grid-cols-2">
        {/* Area B: Sector Heatmap & Movers */}
        <div className="space-y-4">
          <SectorHeatmap
            sectors={marketData.sectors}
            loading={marketData.loading}
            onSectorClick={setSelectedSector}
          />
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

        {/* Area C: News Impact & Calendar */}
        <div className="space-y-4">
          <NewsImpactFeed
            articles={newsData.articles}
            impacts={newsData.impacts}
            loading={newsData.loading}
          />
          <EconomicCalendar
            indicators={marketData.indicators}
            loading={marketData.loading}
          />
        </div>
      </main>

      {/* Area D: Deep Dive & Screener */}
      <section className="mx-4 mb-4 rounded-xl border border-border bg-card p-4">
        <h2 className="mb-2 text-sm font-semibold text-muted-foreground">
          Interactive Deep Dive & AI Screener
        </h2>
        <p className="text-xs text-muted-foreground">Phase 4c에서 구현</p>
      </section>

      {/* Disclaimer */}
      <footer className="border-t border-border px-4 py-3 text-center text-xs text-muted-foreground">
        본 분석은 AI의 추론이며, 실제 투자 판단의 근거로 사용할 수 없습니다.
      </footer>
    </div>
  );
}
