import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import { getImpactColor } from "@/lib/utils";
import type { NewsArticle, NewsImpactAnalysis } from "@/types";

interface ImpactCardProps {
  article: NewsArticle;
  impact?: NewsImpactAnalysis;
}

function timeAgo(dateStr: string): string {
  const diff = Date.now() - new Date(dateStr).getTime();
  const hours = Math.floor(diff / 3600000);
  if (hours < 1) return "방금 전";
  if (hours < 24) return `${hours}시간 전`;
  const days = Math.floor(hours / 24);
  return `${days}일 전`;
}

export function ImpactCard({ article, impact }: ImpactCardProps) {
  return (
    <a
      href={article.url}
      target="_blank"
      rel="noopener noreferrer"
      className="block rounded-lg border border-border p-3 transition-colors hover:bg-muted/30"
    >
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0 flex-1">
          <h4 className="line-clamp-2 text-sm font-medium text-foreground">
            {article.title}
          </h4>
          <div className="mt-1 flex items-center gap-2 text-xs text-muted-foreground">
            <span>{article.source}</span>
            <span>·</span>
            <span>{timeAgo(article.published_at)}</span>
          </div>
          {article.summary && (
            <p className="mt-1 line-clamp-2 text-xs text-muted-foreground">
              {article.summary}
            </p>
          )}
        </div>

        {impact && (
          <div className="flex shrink-0 flex-col items-end gap-1">
            <span
              className={cn(
                "inline-flex h-6 w-6 items-center justify-center rounded-full text-xs font-bold",
                getImpactColor(impact.impact_score),
              )}
            >
              {impact.impact_score}
            </span>
            <Badge
              variant={impact.impact_direction === "positive" ? "bullish" : "bearish"}
              className="text-[10px]"
            >
              {impact.sector_name}
            </Badge>
          </div>
        )}
      </div>
    </a>
  );
}
