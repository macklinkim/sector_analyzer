import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/utils";
import { ImpactCard } from "./ImpactCard";
import type { NewsArticle, NewsImpactAnalysis } from "@/types";

interface NewsImpactFeedProps {
  articles: NewsArticle[];
  impacts: NewsImpactAnalysis[];
  loading: boolean;
}

const TABS = [
  { key: "all", label: "전체" },
  { key: "business", label: "경제" },
  { key: "technology", label: "기술" },
  { key: "science", label: "과학" },
  { key: "general", label: "글로벌" },
] as const;

export function NewsImpactFeed({ articles, impacts, loading }: NewsImpactFeedProps) {
  const [activeTab, setActiveTab] = useState<string>("all");

  const filteredArticles =
    activeTab === "all"
      ? articles
      : articles.filter((a) => a.category === activeTab);

  const impactMap = new Map(impacts.map((imp) => [imp.news_url, imp]));

  return (
    <Card className="flex h-full flex-col">
      <CardHeader className="pb-2">
        <CardTitle>News Impact Feed</CardTitle>
        <div className="flex gap-1 pt-1">
          {TABS.map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key)}
              className={cn(
                "rounded-md px-2.5 py-1 text-xs font-medium transition-colors",
                activeTab === tab.key
                  ? "bg-foreground/10 text-foreground"
                  : "text-muted-foreground hover:text-foreground",
              )}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </CardHeader>
      <CardContent className="flex-1 space-y-2 overflow-y-auto">
        {loading ? (
          Array.from({ length: 5 }).map((_, i) => (
            <Skeleton key={i} className="h-20 w-full" />
          ))
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
