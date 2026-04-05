import { MomentumBar } from "./MomentumBar";
import { RelativeStrength } from "./RelativeStrength";
import { RangeChart } from "./RangeChart";
import { EventMarker } from "./EventMarker";
import type { RotationSignal, Sector } from "@/types";

interface MultiChartGridProps {
  sectors: Sector[];
  signals: RotationSignal[];
  loading: boolean;
}

export function MultiChartGrid({ sectors, signals, loading }: MultiChartGridProps) {
  return (
    <div className="space-y-4">
      <EventMarker signals={signals} />
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <MomentumBar sectors={sectors} loading={loading} />
        <RelativeStrength sectors={sectors} loading={loading} />
      </div>
      <RangeChart sectors={sectors} loading={loading} />
    </div>
  );
}
