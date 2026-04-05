import { useMarketData } from "@/hooks/useMarketData";
import { GlobalMacroHeader } from "@/components/header/GlobalMacroHeader";

export default function App() {
  const marketData = useMarketData();

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
        <section className="rounded-xl border border-border bg-card p-4">
          <h2 className="mb-2 text-sm font-semibold text-muted-foreground">
            Sector Heatmap & Market Movers
          </h2>
          <p className="text-xs text-muted-foreground">Phase 4b에서 구현</p>
        </section>

        {/* Area C: News Impact & Calendar */}
        <section className="rounded-xl border border-border bg-card p-4">
          <h2 className="mb-2 text-sm font-semibold text-muted-foreground">
            News Impact & Calendar
          </h2>
          <p className="text-xs text-muted-foreground">Phase 4b에서 구현</p>
        </section>
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
