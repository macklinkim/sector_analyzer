import { useState } from "react";
import { AdminUsersModal } from "@/components/auth/AdminUsersModal";
import { AvatarLightbox } from "@/components/auth/AvatarLightbox";
import { LoginGate, LoginSplash, logout, useAuth } from "@/components/auth/LoginGate";
import { CryptoTab } from "@/components/crypto/CryptoTab";
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
  const { identity, isAdmin, photoUrl, refresh } = useAuth();
  const [adminOpen, setAdminOpen] = useState(false);
  const [lightboxOpen, setLightboxOpen] = useState(false);
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
        <DashboardTabs
          activeTab={activeTab}
          onChange={setActiveTab}
          identity={identity}
          photoUrl={photoUrl}
          onAvatarClick={identity ? () => setLightboxOpen(true) : undefined}
          avatarTitle={identity ?? undefined}
        />
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
        {activeTab === "crypto" && <CryptoTab />}
      </main>

      <LoginSplash />
      <AvatarLightbox
        open={lightboxOpen}
        onClose={() => setLightboxOpen(false)}
        identity={identity ?? ""}
        photoUrl={photoUrl}
        isAdmin={isAdmin}
        onOpenAdmin={() => setAdminOpen(true)}
      />
      {isAdmin && (
        <AdminUsersModal
          open={adminOpen}
          onClose={() => {
            setAdminOpen(false);
            void refresh();
          }}
          currentIdentity={identity ?? ""}
        />
      )}

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
