import { cn } from "@/lib/utils";

interface Tab {
  id: string;
  label: string;
}

interface TabNavigationProps {
  tabs: Tab[];
  activeTab: string;
  onTabChange: (tabId: string) => void;
}

export function TabNavigation({ tabs, activeTab, onTabChange }: TabNavigationProps) {
  return (
    <nav className="border-b border-cyber-border bg-card">
      <div className="flex">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => onTabChange(tab.id)}
            className={cn(
              "flex-1 py-3 text-center font-medium transition-all duration-200 hover-lift relative",
              activeTab === tab.id
                ? "text-primary border-b-2 border-primary bg-primary/5 shadow-sm"
                : "text-muted-foreground hover:text-foreground hover:bg-muted/50"
            )}
            data-testid={`tab-${tab.id}`}
          >
            {tab.label}
          </button>
        ))}
      </div>
    </nav>
  );
}
