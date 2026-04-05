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
}

function CustomTreemapContent({ x, y, width, height, name, change_percent }: TreemapContentProps) {
  if (width < 40 || height < 30) return null;

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
      {width > 60 && (
        <>
          <text
            x={x + width / 2}
            y={y + height / 2 - 6}
            textAnchor="middle"
            fill="white"
            fontSize={width > 100 ? 12 : 10}
            fontWeight="bold"
          >
            {getSectorLabel(name)}
          </text>
          <text
            x={x + width / 2}
            y={y + height / 2 + 10}
            textAnchor="middle"
            fill="white"
            fontSize={10}
          >
            {formatPercent(change_percent)}
          </text>
        </>
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
            content={<CustomTreemapContent x={0} y={0} width={0} height={0} name="" change_percent={0} />}
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
