import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ReferenceArea,
  ReferenceLine,
  ResponsiveContainer,
  LabelList,
} from "recharts";
import type { Sector } from "@/types";

interface RelativeRotationGraphProps {
  sectors: Sector[];
  loading?: boolean;
}

interface RRGPoint {
  name: string;
  etf: string;
  rsRatio: number;
  rsMomentum: number;
  quadrant: "Leading" | "Improving" | "Weakening" | "Lagging";
}

function classifyQuadrant(rs: number, mom: number): RRGPoint["quadrant"] {
  if (rs >= 0 && mom >= 0) return "Leading";
  if (rs < 0 && mom >= 0) return "Improving";
  if (rs >= 0 && mom < 0) return "Weakening";
  return "Lagging";
}

const QUADRANT_COLORS = {
  Leading: "#22c55e",
  Improving: "#3b82f6",
  Weakening: "#eab308",
  Lagging: "#ef4444",
} as const;

function CustomTooltip({ active, payload }: { active?: boolean; payload?: Array<{ payload: RRGPoint }> }) {
  if (!active || !payload?.length) return null;
  const d = payload[0].payload;
  return (
    <div className="rounded border border-border bg-card px-3 py-2 text-xs shadow-lg">
      <p className="font-bold text-foreground">{d.etf} — {d.name}</p>
      <p className="text-muted-foreground">
        RS-Ratio: <span className="font-mono text-foreground">{d.rsRatio.toFixed(2)}%</span>
      </p>
      <p className="text-muted-foreground">
        RS-Momentum: <span className="font-mono text-foreground">{d.rsMomentum.toFixed(2)}%</span>
      </p>
      <p style={{ color: QUADRANT_COLORS[d.quadrant] }} className="mt-1 font-semibold">
        {d.quadrant}
      </p>
    </div>
  );
}

export function RelativeRotationGraph({ sectors, loading }: RelativeRotationGraphProps) {
  if (loading) {
    return (
      <div className="rounded-lg border border-border bg-card p-4">
        <div className="h-[400px] animate-pulse rounded bg-muted" />
      </div>
    );
  }

  // Deduplicate by etf_symbol (take first occurrence)
  const seen = new Set<string>();
  const deduped = sectors.filter((s) => {
    if (seen.has(s.etf_symbol)) return false;
    seen.add(s.etf_symbol);
    return true;
  });

  const points: RRGPoint[] = deduped
    .filter((s) => s.relative_strength != null && s.momentum_1w != null)
    .map((s) => ({
      name: s.name,
      etf: s.etf_symbol,
      rsRatio: Number(s.relative_strength),
      rsMomentum: Number(s.momentum_1w),
      quadrant: classifyQuadrant(Number(s.relative_strength), Number(s.momentum_1w)),
    }));

  if (points.length === 0) {
    return (
      <div className="rounded-lg border border-border bg-card p-4 text-center text-sm text-muted-foreground">
        RRG 데이터 없음
      </div>
    );
  }

  // Calculate axis range with padding
  const allRs = points.map((p) => p.rsRatio);
  const allMom = points.map((p) => p.rsMomentum);
  const pad = 2;
  const xMin = Math.min(...allRs, -1) - pad;
  const xMax = Math.max(...allRs, 1) + pad;
  const yMin = Math.min(...allMom, -1) - pad;
  const yMax = Math.max(...allMom, 1) + pad;

  return (
    <div className="rounded-lg border border-border bg-card p-4">
      <h3 className="mb-3 text-sm font-semibold text-muted-foreground tracking-wide uppercase">
        Relative Rotation Graph (RRG)
      </h3>
      <div className="relative">
        {/* Quadrant labels — absolute positioned corners */}
        <div className="pointer-events-none absolute inset-0 z-10">
          <span className="absolute right-14 top-10 text-[11px] font-medium text-green-500/40">
            Leading
          </span>
          <span className="absolute left-14 top-10 text-[11px] font-medium text-blue-500/40">
            Improving
          </span>
          <span className="absolute right-14 bottom-10 text-[11px] font-medium text-yellow-500/40">
            Weakening
          </span>
          <span className="absolute left-14 bottom-10 text-[11px] font-medium text-red-500/40">
            Lagging
          </span>
        </div>

        <ResponsiveContainer width="100%" height={400}>
          <ScatterChart margin={{ top: 20, right: 30, bottom: 20, left: 10 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" opacity={0.3} />

            {/* Background quadrant colors */}
            <ReferenceArea x1={0} x2={xMax} y1={0} y2={yMax} fill="#22c55e" fillOpacity={0.05} />
            <ReferenceArea x1={xMin} x2={0} y1={0} y2={yMax} fill="#3b82f6" fillOpacity={0.05} />
            <ReferenceArea x1={0} x2={xMax} y1={yMin} y2={0} fill="#eab308" fillOpacity={0.05} />
            <ReferenceArea x1={xMin} x2={0} y1={yMin} y2={0} fill="#ef4444" fillOpacity={0.05} />

            {/* Center crosshair */}
            <ReferenceLine x={0} stroke="var(--color-border)" strokeWidth={1.5} />
            <ReferenceLine y={0} stroke="var(--color-border)" strokeWidth={1.5} />

            <XAxis
              type="number"
              dataKey="rsRatio"
              domain={[xMin, xMax]}
              tickFormatter={(v: number) => v.toFixed(2)}
              tick={{ fontSize: 10, fill: "var(--color-muted-foreground)" }}
              label={{ value: "RS-Ratio (%)", position: "bottom", fontSize: 11, fill: "var(--color-muted-foreground)" }}
            />
            <YAxis
              type="number"
              dataKey="rsMomentum"
              domain={[yMin, yMax]}
              tickFormatter={(v: number) => v.toFixed(2)}
              tick={{ fontSize: 10, fill: "var(--color-muted-foreground)" }}
              label={{ value: "RS-Momentum (%)", angle: -90, position: "insideLeft", fontSize: 11, fill: "var(--color-muted-foreground)" }}
            />
            <Tooltip content={<CustomTooltip />} />

            {/* One scatter per quadrant for color coding */}
            {(["Leading", "Improving", "Weakening", "Lagging"] as const).map((q) => {
              const data = points.filter((p) => p.quadrant === q);
              if (data.length === 0) return null;
              return (
                <Scatter
                  key={q}
                  data={data}
                  fill={QUADRANT_COLORS[q]}
                  fillOpacity={0.9}
                  r={6}
                >
                  <LabelList
                    dataKey="etf"
                    position="top"
                    offset={10}
                    style={{
                      fontSize: 11,
                      fontWeight: 600,
                      fill: QUADRANT_COLORS[q],
                    }}
                  />
                </Scatter>
              );
            })}
          </ScatterChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
