import { useState } from "react";
import { LoginGate, logout, useAuth } from "@/components/auth/LoginGate";
import { useAnalysisData } from "@/hooks/useAnalysisData";
import { useMarketData } from "@/hooks/useMarketData";
import { useNewsData } from "@/hooks/useNewsData";
import { LoadingScreen } from "@/components/ui/LoadingScreen";
import { GlobalMacroHeader } from "@/components/header/GlobalMacroHeader";
import { SectorHeatmap } from "@/components/sector/SectorHeatmap";
import { SectorSparkline } from "@/components/sector/SectorSparkline";
import { MarketMovers } from "@/components/sector/MarketMovers";
import { SectorStockTreemap } from "@/components/sector/SectorStockTreemap";
import { NewsImpactFeed } from "@/components/news/NewsImpactFeed";
import { EconomicCalendar } from "@/components/news/EconomicCalendar";
import { MultiChartGrid } from "@/components/chart/MultiChartGrid";
import { AiScreenerTable } from "@/components/screener/AiScreenerTable";

function Dashboard() {
  const { name } = useAuth();
  const marketData = useMarketData();
  const newsData = useNewsData();
  const analysisData = useAnalysisData();
  const [selectedSector, setSelectedSector] = useState<string | null>(null);
  const selectedEtf = marketData.sectors.find((s) => s.name === selectedSector)?.etf_symbol ?? null;

  const isLoading = marketData.loading || newsData.loading;

  return (
    <div className="min-h-screen bg-background text-foreground">
      {isLoading && <LoadingScreen />}
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
          <SectorStockTreemap
            selectedSector={selectedSector}
            etfSymbol={selectedEtf}
          />
          <SectorSparkline
            sectors={marketData.sectors}
            selectedSector={selectedSector}
            onSectorClick={setSelectedSector}
          />
        </div>

        {/* Area C: News Impact & Calendar & Rankings */}
        <div className="space-y-4">
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
          <MarketMovers
            sectors={marketData.sectors}
            selectedSector={selectedSector}
          />
        </div>
      </main>

      {/* Area D: Deep Dive & Screener */}
      <section className="space-y-4 px-4 pb-4">
        <MultiChartGrid
          sectors={marketData.sectors}
          signals={analysisData.signals}
          loading={marketData.loading}
        />
        <AiScreenerTable
          scoreboards={analysisData.scoreboards}
          loading={analysisData.loading}
        />
      </section>

      {/* Footer */}
      <footer className="border-t border-border px-4 py-3">
        <div className="flex items-center justify-between">
          <span className="text-xs text-muted-foreground">
            본 분석은 AI의 추론이며, 실제 투자 판단의 근거로 사용할 수 없습니다.
          </span>
          <div className="flex items-center gap-3">
            <span className="text-xs text-muted-foreground">{name}</span>
            <button
              onClick={logout}
              className="text-xs text-muted-foreground underline hover:text-foreground"
            >
              로그아웃
            </button>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default function App() {
  return (
    <LoginGate>
      <Dashboard />
    </LoginGate>
  );
}
