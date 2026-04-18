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
    <div className="flex justify-center border-b-2 border-border bg-background px-2 py-1 sm:px-4 sm:py-3">
      <div
        role="tablist"
        aria-label="대시보드 탭"
        className="inline-flex gap-1 rounded-lg bg-muted/80 p-0.5 shadow-inner sm:rounded-xl sm:p-1.5"
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
                "relative rounded-md px-5 py-1 text-xs font-semibold tracking-wide transition-all sm:rounded-lg sm:px-8 sm:py-2.5 sm:text-base",
                "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2",
                active
                  ? "bg-background text-foreground shadow-md"
                  : "text-muted-foreground hover:bg-muted hover:text-foreground",
              )}
            >
              {tab.label}
              {active && (
                <span className="absolute inset-x-3 -bottom-1 h-0.5 rounded-full bg-primary sm:-bottom-1.5" />
              )}
            </button>
          );
        })}
      </div>
    </div>
  );
}
