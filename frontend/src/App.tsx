import { useState } from "react";
import { LoginGate, logout, useAuth } from "@/components/auth/LoginGate";
import { GlobalMacroHeader } from "@/components/header/GlobalMacroHeader";
import { AiTab } from "@/components/layout/AiTab";
import { DashboardTabs } from "@/components/layout/DashboardTabs";
import { MarketTab } from "@/components/layout/MarketTab";
import { useAnalysisData } from "@/hooks/useAnalysisData";
import { useMarketData } from "@/hooks/useMarketData";
import { useNewsData } from "@/hooks/useNewsData";
import { useStickyState } from "@/hooks/useStickyState";
import type { DashboardTab } from "@/types";

function Dashboard() {
  const { identity } = useAuth();
  const marketData = useMarketData();
  const newsData = useNewsData();
  const analysisData = useAnalysisData();
  const [activeTab, setActiveTab] = useStickyState<DashboardTab>(
    "dashboard_active_tab",
    "market",
  );
  const [selectedSector, setSelectedSector] = useState<string | null>(null);

  return (
    <div className="min-h-screen bg-background text-foreground">
      {/* Sticky top: GlobalMacroHeader + DashboardTabs */}
      <div className="sticky top-0 z-40 bg-background">
        <header>
          <GlobalMacroHeader
            indices={marketData.indices}
            indicators={marketData.indicators}
            regime={marketData.regime}
            loading={marketData.loading}
            lastUpdated={marketData.lastUpdated}
          />
        </header>
        <DashboardTabs activeTab={activeTab} onChange={setActiveTab} />
      </div>

      <main>
        {activeTab === "market" && (
          <MarketTab
            marketData={marketData}
            newsData={newsData}
            selectedSector={selectedSector}
            setSelectedSector={setSelectedSector}
          />
        )}
        {activeTab === "ai" && (
          <AiTab
            marketData={marketData}
            analysisData={analysisData}
            selectedSector={selectedSector}
            setSelectedSector={setSelectedSector}
          />
        )}
      </main>

      <footer className="border-t border-border px-4 py-3">
        <div className="flex items-center justify-between">
          <span className="text-xs text-muted-foreground">
            본 분석은 AI의 추론이며, 실제 투자 판단의 근거로 사용할 수 없습니다.
          </span>
          <div className="flex items-center gap-3">
            <span className="text-xs text-muted-foreground">{identity}</span>
            <button
              type="button"
              onClick={() => {
                void logout();
              }}
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
