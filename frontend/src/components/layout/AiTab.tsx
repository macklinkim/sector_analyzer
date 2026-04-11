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
      {/* Row 1: BusinessCycleClock — 단독 풀폭 중앙정렬 (확대된 사이즈) */}
      <div className="flex justify-center">
        <div className="w-full max-w-2xl">
          <BusinessCycleClock
            regime={marketData.regime}
            loading={marketData.loading}
          />
        </div>
      </div>

      {/* Row 2: RelativeRotationGraph — 풀폭 */}
      <RelativeRotationGraph
        sectors={marketData.sectors}
        loading={marketData.loading}
      />

      {/* Row 3: AI Rotation Signals (풀폭) — 판단 */}
      <AiRotationSignals signals={analysisData.signals} />

      {/* Row 4: AI Sector Screener (풀폭) — 실행 */}
      <AiScreenerTable
        scoreboards={analysisData.scoreboards}
        loading={analysisData.loading}
        selectedSector={selectedSector}
        onSectorClick={setSelectedSector}
      />
    </div>
  );
}
