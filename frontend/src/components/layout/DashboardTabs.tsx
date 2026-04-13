import type { DashboardTab } from "@/types";
import { cn } from "@/lib/utils";

interface DashboardTabsProps {
  activeTab: DashboardTab;
  onChange: (tab: DashboardTab) => void;
}

interface TabDef {
  id: DashboardTab;
  label: string;
}

const TABS: TabDef[] = [
  { id: "market", label: "시장 현황" },
  { id: "ai", label: "AI 인사이트" },
];

export function DashboardTabs({ activeTab, onChange }: DashboardTabsProps) {
  return (
    <div className="flex justify-center border-b border-border bg-background px-4 py-2">
      <div
        role="tablist"
        aria-label="대시보드 탭"
        className="inline-flex rounded-lg bg-muted p-1"
      >
        {TABS.map((tab) => {
          const active = tab.id === activeTab;
          return (
            <button
              key={tab.id}
              type="button"
              role="tab"
              id={`tab-${tab.id}`}
              aria-selected={active}
              aria-controls={`panel-${tab.id}`}
              onClick={() => onChange(tab.id)}
              className={cn(
                "rounded-md px-6 py-2 text-sm font-medium transition-all",
                "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2",
                active
                  ? "bg-background text-foreground shadow-sm"
                  : "text-muted-foreground hover:text-foreground",
              )}
            >
              {tab.label}
            </button>
          );
        })}
      </div>
    </div>
  );
}
