import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import { getImpactColor } from "@/lib/utils";
import type { NewsArticleEnriched, NewsImpactAnalysis } from "@/types";

interface ImpactCardProps {
  article: NewsArticleEnriched;
  impact?: NewsImpactAnalysis;
}

function timeAgo(dateStr: string | null | undefined): string {
  if (!dateStr) return "";
  const time = new Date(dateStr).getTime();
  if (isNaN(time)) return "";
  const diff = Date.now() - time;
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

const CATEGORY_STYLE: Record<string, { label: string; color: string }> = {
  A_MACRO: { label: "매크로", color: "bg-red-500/20 text-red-400" },
  B_INDUSTRY: { label: "산업", color: "bg-amber-500/20 text-amber-400" },
  C_CORPORATE: { label: "기업", color: "bg-blue-500/20 text-blue-400" },
};

export function ImpactCard({ article, impact }: ImpactCardProps) {
  const catStyle = article.news_category ? CATEGORY_STYLE[article.news_category] : null;
  const score = impact?.impact_score ?? article.impact_score;

  // Hide noise (no summary and score 0)
  if (!article.summary_ko && score === 0) return null;

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
            <span>{timeAgo(article.published_at ?? article.analyzed_at)}</span>
          </div>

          {article.summary_ko && (
            <p className="mt-1.5 text-xs leading-relaxed text-card-foreground">
              {article.summary_ko}
              {article.impact_label && (
                <span className={cn("ml-1 font-medium", getImpactLabelColor(article.impact_label))}>
                  [{article.impact_label} {score}/10
                  {article.related_sector ? ` · ${article.related_sector}` : ""}]
                </span>
              )}
            </p>
          )}

          {/* Expert Insight */}
          {article.expert_insight && (
            <p className="mt-1 text-[11px] leading-relaxed text-amber-400/80">
              {article.expert_insight}
            </p>
          )}

          {/* Action Item */}
          {article.action_item && (
            <p className="mt-0.5 text-[11px] text-muted-foreground">
              <span className="font-medium text-foreground/70">Action:</span> {article.action_item}
            </p>
          )}

          {!article.summary_ko && article.summary && (
            <p className="mt-1 line-clamp-2 text-xs text-muted-foreground">
              {article.summary}
            </p>
          )}
        </div>

        {score > 0 && (
          <div className="flex shrink-0 flex-col items-end gap-1">
            <span
              className={cn(
                "inline-flex h-6 w-6 items-center justify-center rounded-full text-xs font-bold",
                getImpactColor(score),
              )}
            >
              {score}
            </span>
            {catStyle && (
              <span className={cn("rounded px-1.5 py-0.5 text-[10px] font-medium", catStyle.color)}>
                {catStyle.label}
              </span>
            )}
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
