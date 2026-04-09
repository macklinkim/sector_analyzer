import { useCallback, useEffect, useState } from "react";
import { Treemap, ResponsiveContainer } from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { getSectorLabel } from "@/lib/i18n";
import { formatPercent, getCached, setCache } from "@/lib/utils";
import { api } from "@/lib/api";

interface StockData {
  symbol: string;
  name: string;
  close: number;
  change_p: number;
  volume: number;
  market_cap: number;
}

interface SectorStockTreemapProps {
  selectedSector: string | null;
  etfSymbol: string | null;
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
  companyName: string;
  change_p: number;
  close: number;
}

function CustomContent({ x, y, width, height, name, companyName, change_p }: TreemapContentProps) {
  if (width < 35 || height < 25) return null;

  const shortName = companyName ? companyName.slice(0, 7) : "";

  return (
    <g>
      <rect
        x={x} y={y} width={width} height={height} rx={3}
        fill={getHeatmapColor(change_p)}
        stroke="var(--color-background)" strokeWidth={2}
      />
      {width > 50 && (
        <>
          <text x={x + width / 2} y={y + height / 2 - (shortName ? 12 : 8)} textAnchor="middle"
            fill="white" fontSize={width > 80 ? 11 : 9} fontWeight="bold">
            {name}
          </text>
          {shortName && (
            <text x={x + width / 2} y={y + height / 2 - 1} textAnchor="middle"
              fill="rgba(255,255,255,0.6)" fontSize={7}>
              {shortName}
            </text>
          )}
          <text x={x + width / 2} y={y + height / 2 + 10} textAnchor="middle"
            fill="rgba(255,255,255,0.8)" fontSize={8}>
            {formatPercent(change_p)}
          </text>
        </>
      )}
    </g>
  );
}

export function SectorStockTreemap({ selectedSector, etfSymbol }: SectorStockTreemapProps) {
  const [stocks, setStocks] = useState<StockData[]>([]);
  const [loading, setLoading] = useState(false);

  const fetchStocks = useCallback(async () => {
    if (!etfSymbol) return;

    const cacheKey = `sector_stocks_${etfSymbol}`;
    const cached = getCached<StockData[]>(cacheKey);
    if (cached) {
      setStocks(cached);
      return;
    }

    setLoading(true);
    try {
      const data = await api.getSectorStocks(etfSymbol);
      setStocks(data);
      setCache(cacheKey, data);
    } catch {
      // ignore
    } finally {
      setLoading(false);
    }
  }, [etfSymbol]);

  useEffect(() => {
    fetchStocks();
  }, [fetchStocks]);

  if (!selectedSector) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>섹터 구성종목</CardTitle>
        </CardHeader>
        <CardContent className="py-8 text-center text-sm text-muted-foreground">
          섹터를 클릭하면 구성종목 히트맵을 표시합니다
        </CardContent>
      </Card>
    );
  }

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>{getSectorLabel(selectedSector)} 구성종목</CardTitle>
        </CardHeader>
        <CardContent>
          <Skeleton className="h-56 w-full" />
        </CardContent>
      </Card>
    );
  }

  const treemapData = stocks
    .filter((s) => s.symbol !== "ETC" && s.close > 0)
    .map((s) => ({
      name: s.symbol,
      companyName: s.name,
      size: s.market_cap || s.volume || 1,
      change_p: s.change_p,
      close: s.close,
    }));

  const etc = stocks.find((s) => s.symbol === "ETC");
  if (etc) {
    treemapData.push({
      name: etc.name,
      companyName: "",
      size: 1,
      change_p: 0,
      close: 0,
    });
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>{getSectorLabel(selectedSector)} 구성종목 ({etfSymbol})</CardTitle>
      </CardHeader>
      <CardContent>
        {treemapData.length === 0 ? (
          <p className="py-8 text-center text-sm text-muted-foreground">데이터 없음</p>
        ) : (
          <ResponsiveContainer width="100%" height={240}>
            <Treemap
              data={treemapData}
              dataKey="size"
              stroke="none"
              content={<CustomContent x={0} y={0} width={0} height={0} name="" companyName="" change_p={0} close={0} />}
            />
          </ResponsiveContainer>
        )}
      </CardContent>
    </Card>
  );
}
