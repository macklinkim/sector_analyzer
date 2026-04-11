import { MomentumBar } from "./MomentumBar";
import { RangeChart } from "./RangeChart";
import { RelativeStrength } from "./RelativeStrength";
import type { Sector } from "@/types";

interface SectorComparisonChartsProps {
  sectors: Sector[];
  loading: boolean;
}

/**
 * Tab 1 "시장 현황"의 섹터 비교 차트 3종을 세로 풀폭 스택으로 렌더한다.
 * 기존 MultiChartGrid에서 EventMarker(AI 시그널)는 제거되어 Tab 2의
 * AiRotationSignals로 분리되었다.
 */
export function SectorComparisonCharts({
  sectors,
  loading,
}: SectorComparisonChartsProps) {
  return (
    <div className="space-y-4">
      <RelativeStrength sectors={sectors} loading={loading} />
      <MomentumBar sectors={sectors} loading={loading} />
      <RangeChart sectors={sectors} loading={loading} />
    </div>
  );
}
