import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import { getImpactColor } from "@/lib/utils";
import type { NewsArticleEnriched, NewsImpactAnalysis } from "@/types";

interface ImpactCardProps {
  article: NewsArticleEnriched;
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

function getImpactLabelColor(label: string | null): string {
  if (!label) return "text-muted-foreground";
  if (label === "긍정") return "text-bullish";
  if (label === "부정") return "text-bearish";
  return "text-muted-foreground";
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
          {/* Korean AI Summary */}
          {article.summary_ko && (
            <p className="mt-1.5 text-xs leading-relaxed text-card-foreground">
              {article.summary_ko}
              {article.impact_label && (
                <span className={cn("ml-1 font-medium", getImpactLabelColor(article.impact_label))}>
                  [{article.impact_label} {article.impact_score}/10
                  {article.related_sector ? ` · ${article.related_sector}` : ""}]
                </span>
              )}
            </p>
          )}
          {/* Fallback: English summary if no Korean */}
          {!article.summary_ko && article.summary && (
            <p className="mt-1 line-clamp-2 text-xs text-muted-foreground">
              {article.summary}
            </p>
          )}
        </div>

        {(impact || article.impact_score > 0) && (
          <div className="flex shrink-0 flex-col items-end gap-1">
            <span
              className={cn(
                "inline-flex h-6 w-6 items-center justify-center rounded-full text-xs font-bold",
                getImpactColor(impact?.impact_score ?? article.impact_score),
              )}
            >
              {impact?.impact_score ?? article.impact_score}
            </span>
            {article.related_sector && (
              <Badge variant="default" className="text-[10px]">
                {article.related_sector}
              </Badge>
            )}
          </div>
        )}
      </div>
    </a>
  );
}
