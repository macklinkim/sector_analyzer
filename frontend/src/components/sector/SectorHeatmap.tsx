import { Treemap, ResponsiveContainer } from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { getSectorLabel } from "@/lib/i18n";
import { formatPercent } from "@/lib/utils";
import type { Sector } from "@/types";

interface SectorHeatmapProps {
  sectors: Sector[];
  loading: boolean;
  onSectorClick?: (sectorName: string) => void;
}

function getHeatmapColor(changePercent: number): string {
  if (changePercent >= 2) return "#15803d";
  if (changePercent >= 1) return "#16a34a";
  if (changePercent > 0) return "#22c55e";
  if (changePercent === 0) return "#6b7280";
  if (changePercent > -1) return "#ef4444";
  if (changePercent > -2) return "#dc2626";
  return "#b91c1c";
}

interface TreemapContentProps {
  x: number;
  y: number;
  width: number;
  height: number;
  name: string;
  change_percent: number;
  etf_symbol?: string;
}

function CustomTreemapContent({ x, y, width, height, name, change_percent, etf_symbol }: TreemapContentProps) {
  if (width < 18 || height < 16) return null;

  // Narrow cells show the ETF ticker (e.g. XLK) — more identifiable than a
  // truncated Korean label. Wider cells can fit the full sector name.
  const useTicker = width < 60;
  const primary = useTicker && etf_symbol ? etf_symbol : getSectorLabel(name);
  const nameSize = width > 100 ? 12 : width > 60 ? 10 : width > 36 ? 9 : 8;
  const pctSize = width > 60 ? 10 : width > 36 ? 8 : 7;
  const showPct = height >= 30;

  return (
    <g>
      <rect
        x={x}
        y={y}
        width={width}
        height={height}
        rx={4}
        fill={getHeatmapColor(change_percent)}
        stroke="var(--color-background)"
        strokeWidth={2}
      />
      <text
        x={x + width / 2}
        y={y + height / 2 - (showPct ? 6 : 0)}
        textAnchor="middle"
        fill="white"
        fontSize={nameSize}
        fontWeight="bold"
      >
        {primary}
      </text>
      {showPct && (
        <text
          x={x + width / 2}
          y={y + height / 2 + 10}
          textAnchor="middle"
          fill="white"
          fontSize={pctSize}
        >
          {formatPercent(change_percent)}
        </text>
      )}
    </g>
  );
}

export function SectorHeatmap({ sectors, loading, onSectorClick }: SectorHeatmapProps) {
  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Sector Heatmap</CardTitle>
        </CardHeader>
        <CardContent>
          <Skeleton className="h-64 w-full" />
        </CardContent>
      </Card>
    );
  }

  const treemapData = sectors.map((s) => ({
    name: s.name,
    size: s.volume || 1,
    change_percent: s.change_percent,
    etf_symbol: s.etf_symbol,
  }));

  return (
    <Card>
      <CardHeader>
        <CardTitle>Sector Heatmap</CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={280}>
          <Treemap
            data={treemapData}
            dataKey="size"
            stroke="none"
            content={<CustomTreemapContent x={0} y={0} width={0} height={0} name="" change_percent={0} etf_symbol="" />}
            onClick={(node) => {
              if (onSectorClick && node?.name) {
                onSectorClick(node.name as string);
              }
            }}
          />
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
