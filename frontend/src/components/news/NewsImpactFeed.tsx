import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/utils";
import { getCategoryLabel } from "@/lib/i18n";
import { getImpactColor } from "@/lib/utils";
import { ImpactCard } from "./ImpactCard";
import type { GlobalCrisis, NewsArticleEnriched, NewsImpactAnalysis } from "@/types";

interface NewsImpactFeedProps {
  articles: NewsArticleEnriched[];
  impacts: NewsImpactAnalysis[];
  crises: GlobalCrisis[];
  loading: boolean;
}

function CrisisCard({ crisis }: { crisis: GlobalCrisis }) {
  const sentimentColor =
    crisis.sentiment === "negative"
      ? "bg-red-500/20 text-red-400"
      : crisis.sentiment === "positive"
        ? "bg-emerald-500/20 text-emerald-400"
        : "bg-gray-500/20 text-gray-400";

  return (
    <div className="rounded-lg border border-border p-3">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0 flex-1">
          <h4 className="line-clamp-1 text-sm font-medium text-foreground">
            {crisis.title}
          </h4>
          <div className="mt-1 flex items-center gap-2 text-xs text-muted-foreground">
            <span>{crisis.source}</span>
            <span>·</span>
            <span>{crisis.time_ago}</span>
          </div>
          <p className="mt-1.5 line-clamp-2 text-xs leading-relaxed text-card-foreground">
            {crisis.summary}
          </p>
        </div>
        <div className="flex shrink-0 flex-col items-end gap-1">
          <span
            className={cn(
              "inline-flex h-7 w-7 items-center justify-center rounded-full text-xs font-bold",
              getImpactColor(crisis.impact_score),
            )}
          >
            {crisis.impact_score}
          </span>
          <span className={cn("rounded px-1.5 py-0.5 text-[10px] font-medium", sentimentColor)}>
            {crisis.affected_sector}
          </span>
        </div>
      </div>
    </div>
  );
}

export function NewsImpactFeed({ articles, impacts, crises, loading }: NewsImpactFeedProps) {
  const [activeTab, setActiveTab] = useState<string>("all");

  const categorySet = new Set(articles.map((a) => a.category));
  const tabs = [
    { key: "all", label: getCategoryLabel("all") },
    ...Array.from(categorySet)
      .sort()
      .map((cat) => ({ key: cat, label: getCategoryLabel(cat) })),
    { key: "crises", label: "글로벌 위기" },
  ];

  const filteredArticles =
    activeTab === "all"
      ? articles
      : articles.filter((a) => a.category === activeTab);

  const impactMap = new Map(impacts.map((imp) => [imp.news_url, imp]));

  return (
    <Card className="flex flex-col">
      <CardHeader className="pb-2">
        <CardTitle>News Impact Feed</CardTitle>
        <div className="flex flex-wrap gap-1 pt-1">
          {tabs.map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key)}
              className={cn(
                "rounded-md px-2.5 py-1 text-xs font-medium transition-colors",
                activeTab === tab.key
                  ? "bg-foreground/10 text-foreground"
                  : "text-muted-foreground hover:text-foreground",
                tab.key === "crises" && "text-red-400 hover:text-red-300",
              )}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </CardHeader>
      <CardContent className="flex-1 min-h-0 space-y-2 overflow-y-auto">
        {loading ? (
          Array.from({ length: 5 }).map((_, i) => (
            <Skeleton key={i} className="h-20 w-full" />
          ))
        ) : activeTab === "crises" ? (
          crises.length === 0 ? (
            <p className="py-8 text-center text-sm text-muted-foreground">
              글로벌 위기 데이터 없음 — 서버에서 뉴스를 수집하지 못했습니다
            </p>
          ) : (
            crises.map((crisis, i) => (
              <CrisisCard key={i} crisis={crisis} />
            ))
          )
        ) : filteredArticles.length === 0 ? (
          <p className="py-8 text-center text-sm text-muted-foreground">
            뉴스가 없습니다
          </p>
        ) : (
          filteredArticles.map((article) => (
            <ImpactCard
              key={article.url}
              article={article}
              impact={impactMap.get(article.url)}
            />
          ))
        )}
      </CardContent>
    </Card>
  );
}
