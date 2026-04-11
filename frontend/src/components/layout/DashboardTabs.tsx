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
    <div
      role="tablist"
      aria-label="대시보드 탭"
      className="flex gap-1 border-b border-border bg-background px-4"
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
              "relative px-4 py-3 text-sm font-medium transition-colors",
              "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2",
              active
                ? "text-foreground"
                : "text-muted-foreground hover:text-foreground",
            )}
          >
            {tab.label}
            {active && (
              <span
                aria-hidden="true"
                className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary"
              />
            )}
          </button>
        );
      })}
    </div>
  );
}
