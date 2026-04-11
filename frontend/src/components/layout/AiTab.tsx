import { AiRotationSignals } from "@/components/chart/AiRotationSignals";
import { BusinessCycleClock } from "@/components/chart/BusinessCycleClock";
import { RelativeRotationGraph } from "@/components/chart/RelativeRotationGraph";
import { AiScreenerTable } from "@/components/screener/AiScreenerTable";
import type { AnalysisDataState, MarketDataState } from "@/types";

interface AiTabProps {
  marketData: MarketDataState;
  analysisData: AnalysisDataState;
  selectedSector: string | null;
  setSelectedSector: (sector: string | null) => void;
}

export function AiTab({
  marketData,
  analysisData,
  selectedSector,
  setSelectedSector,
}: AiTabProps) {
  return (
    <div
      id="panel-ai"
      role="tabpanel"
      aria-labelledby="tab-ai"
      className="space-y-4 p-4"
    >
      {/* Row 1: BCC + RRG (2열) — 맥락 설정 */}
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <BusinessCycleClock
          regime={marketData.regime}
          loading={marketData.loading}
        />
        <RelativeRotationGraph
          sectors={marketData.sectors}
          loading={marketData.loading}
        />
      </div>

      {/* Row 2: AI Rotation Signals (풀폭) — 판단 */}
      <AiRotationSignals signals={analysisData.signals} />

      {/* Row 3: AI Sector Screener (풀폭) — 실행 */}
      <AiScreenerTable
        scoreboards={analysisData.scoreboards}
        loading={analysisData.loading}
        selectedSector={selectedSector}
        onSectorClick={setSelectedSector}
      />
    </div>
  );
}
