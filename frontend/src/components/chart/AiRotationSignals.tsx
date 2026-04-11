import { EventMarker } from "./EventMarker";
import type { RotationSignal } from "@/types";

interface AiRotationSignalsProps {
  signals: RotationSignal[];
}

/**
 * Tab 2 "AI 인사이트"의 "AI Rotation Signals" 위젯.
 * 현재는 EventMarker를 그대로 호출하는 경량 래퍼이며,
 * 향후 AI 시그널 전용 기능(필터/정렬/시간 범위)을 추가할 확장 포인트.
 *
 * EventMarker 내부의 CardTitle은 이미 "AI Rotation Signals"로
 * 설정되어 있으므로 추가 수정 불필요 (verified 2026-04-11).
 */
export function AiRotationSignals({ signals }: AiRotationSignalsProps) {
  return <EventMarker signals={signals} />;
}
