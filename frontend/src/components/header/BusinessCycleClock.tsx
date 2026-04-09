import { motion } from "framer-motion";
import { ArrowRight, TrendingUp, TrendingDown, Flame, Snowflake } from "lucide-react";
import type { MacroRegime, RegimeType } from "@/types";

interface BusinessCycleClockProps {
  regime: MacroRegime | null;
  loading?: boolean;
}

const QUADRANTS: {
  key: RegimeType;
  label: string;
  subtitle: string;
  sectors: string;
  icon: typeof TrendingUp;
  color: string;
  bgColor: string;
  angle: number; // center angle in degrees (12 o'clock = 0)
}[] = [
  {
    key: "goldilocks",
    label: "Goldilocks",
    subtitle: "High Growth · Low Inflation",
    sectors: "XLK · XLY · XLC",
    icon: TrendingUp,
    color: "text-green-400",
    bgColor: "bg-green-500/15",
    angle: 315, // top-left
  },
  {
    key: "reflation",
    label: "Reflation",
    subtitle: "High Growth · High Inflation",
    sectors: "XLI · XLB · XLF",
    icon: Flame,
    color: "text-amber-400",
    bgColor: "bg-amber-500/15",
    angle: 45, // top-right
  },
  {
    key: "stagflation",
    label: "Stagflation",
    subtitle: "Low Growth · High Inflation",
    sectors: "XLE · XLP",
    icon: TrendingDown,
    color: "text-red-400",
    bgColor: "bg-red-500/15",
    angle: 135, // bottom-right
  },
  {
    key: "deflation",
    label: "Deflation",
    subtitle: "Low Growth · Low Inflation",
    sectors: "XLV · XLU",
    icon: Snowflake,
    color: "text-blue-400",
    bgColor: "bg-blue-500/15",
    angle: 225, // bottom-left
  },
];

export function BusinessCycleClock({ regime, loading }: BusinessCycleClockProps) {
  if (loading || !regime) {
    return (
      <div className="rounded-lg border border-border bg-card p-4">
        <div className="h-[280px] animate-pulse rounded bg-muted" />
      </div>
    );
  }

  const currentRegime = regime.regime;
  const probabilities = regime.regime_probabilities ?? {};

  // Find the current quadrant's angle for the pointer
  const currentQuadrant = QUADRANTS.find((q) => q.key === currentRegime);
  const pointerAngle = currentQuadrant?.angle ?? 0;

  return (
    <div className="rounded-lg border border-border bg-card p-4">
      <h3 className="mb-3 text-sm font-semibold text-muted-foreground tracking-wide uppercase">
        Business Cycle Clock
      </h3>

      <div className="relative mx-auto h-[240px] w-[240px]">
        {/* Axis labels */}
        <span className="absolute -top-1 left-1/2 -translate-x-1/2 text-[10px] text-muted-foreground">
          Growth ↑
        </span>
        <span className="absolute -bottom-1 left-1/2 -translate-x-1/2 text-[10px] text-muted-foreground">
          Growth ↓
        </span>
        <span className="absolute top-1/2 -left-2 -translate-y-1/2 text-[10px] text-muted-foreground">
          Infl ↓
        </span>
        <span className="absolute top-1/2 -right-2 -translate-y-1/2 text-[10px] text-muted-foreground">
          Infl ↑
        </span>

        {/* Center circle */}
        <div className="absolute left-1/2 top-1/2 z-10 h-3 w-3 -translate-x-1/2 -translate-y-1/2 rounded-full bg-white/80" />

        {/* Pointer arrow — animated rotation */}
        <motion.div
          className="absolute left-1/2 top-1/2 z-20 origin-bottom"
          style={{ width: 2, height: 80, marginLeft: -1, marginTop: -80 }}
          initial={{ rotate: 0 }}
          animate={{ rotate: pointerAngle }}
          transition={{ type: "spring", stiffness: 60, damping: 15 }}
        >
          <div className="h-full w-full rounded-full bg-white/90" />
          <ArrowRight className="absolute -top-2 left-1/2 h-4 w-4 -translate-x-1/2 -rotate-90 text-white" />
        </motion.div>

        {/* Cross-hair lines */}
        <div className="absolute left-1/2 top-0 h-full w-px -translate-x-1/2 bg-border/50" />
        <div className="absolute left-0 top-1/2 h-px w-full -translate-y-1/2 bg-border/50" />

        {/* 4 Quadrants */}
        {QUADRANTS.map((q) => {
          const isActive = q.key === currentRegime;
          const prob = Math.round((probabilities[q.key] ?? 0) * 100);
          const Icon = q.icon;

          // Position: TL, TR, BR, BL
          const posClass =
            q.angle === 315
              ? "top-1 left-1"
              : q.angle === 45
                ? "top-1 right-1"
                : q.angle === 135
                  ? "bottom-1 right-1"
                  : "bottom-1 left-1";

          return (
            <div
              key={q.key}
              className={`absolute ${posClass} flex h-[116px] w-[116px] flex-col items-center justify-center rounded-lg transition-all ${
                isActive
                  ? `${q.bgColor} ring-1 ring-white/20`
                  : "bg-muted/30 opacity-50"
              }`}
            >
              <Icon className={`mb-1 h-4 w-4 ${isActive ? q.color : "text-muted-foreground"}`} />
              <span className={`text-xs font-bold ${isActive ? q.color : "text-muted-foreground"}`}>
                {q.label}
              </span>
              <span className="mt-0.5 text-[9px] text-muted-foreground leading-tight text-center px-1">
                {q.subtitle}
              </span>
              <span className={`mt-1 text-[10px] font-mono ${isActive ? "text-foreground" : "text-muted-foreground"}`}>
                {prob}%
              </span>
              {isActive && (
                <span className="mt-0.5 text-[9px] font-medium text-muted-foreground">
                  {q.sectors}
                </span>
              )}
            </div>
          );
        })}
      </div>

      {/* Transition info */}
      {regime.transition_from && (
        <div className="mt-2 text-center text-[10px] text-muted-foreground">
          {regime.transition_from} → {currentRegime}
          {regime.transition_probability != null && (
            <span className="ml-1">({Math.round(regime.transition_probability * 100)}%)</span>
          )}
        </div>
      )}
    </div>
  );
}
