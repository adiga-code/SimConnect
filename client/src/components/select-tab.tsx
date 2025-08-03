import { useState } from "react";
import { Plus } from "lucide-react";
import { Button } from "@/components/ui/button";
import { SearchBar } from "@/components/search-bar";
import { TabNavigation } from "@/components/tab-navigation";
import { CountriesTab } from "@/components/countries-tab";
import { ServicesTab } from "@/components/services-tab";
import { PurchaseModal } from "@/components/purchase-modal";
import type { Country, Service } from "@shared/schema";

const tabs = [
  { id: "countries", label: "Страны" },
  { id: "services", label: "Сервисы" },
];

interface SelectTabProps {
  onPurchaseSuccess?: () => void;
}

export function SelectTab({ onPurchaseSuccess }: SelectTabProps) {
  const [activeTab, setActiveTab] = useState("countries");
  const [searchQuery, setSearchQuery] = useState("");
  const [isPurchaseModalOpen, setIsPurchaseModalOpen] = useState(false);

  const handleCountrySelect = (country: Country) => {
    console.log("Selected country:", country);
    setIsPurchaseModalOpen(true);
  };

  const handleServiceSelect = (service: Service) => {
    console.log("Selected service:", service);
    setIsPurchaseModalOpen(true);
  };

  const handlePurchaseModalClose = (open: boolean, success?: boolean) => {
    setIsPurchaseModalOpen(open);
    if (success && onPurchaseSuccess) {
      onPurchaseSuccess();
    }
  };

  const renderTabContent = () => {
    switch (activeTab) {
      case "countries":
        return (
          <CountriesTab 
            searchQuery={searchQuery} 
            onCountrySelect={handleCountrySelect}
          />
        );
      case "services":
        return (
          <ServicesTab 
            searchQuery={searchQuery} 
            onServiceSelect={handleServiceSelect}
          />
        );
      default:
        return null;
    }
  };

  return (
    <div className="flex flex-col h-full animate-fade-in">
      <SearchBar 
        value={searchQuery}
        onChange={setSearchQuery}
        placeholder="Поиск стран или сервисов..."
      />
      
      <TabNavigation 
        tabs={tabs}
        activeTab={activeTab}
        onTabChange={setActiveTab}
      />
      
      <div className="flex-1 relative">
        <div className="animate-fade-in-up">
          {renderTabContent()}
        </div>
        
        {/* Floating Action Button */}
        <div className="fixed bottom-20 right-4 z-40">
          <Button
            size="icon"
            onClick={() => setIsPurchaseModalOpen(true)}
            className="w-14 h-14 bg-primary hover:bg-primary/90 text-primary-foreground rounded-full shadow-cyber btn-cyber hover-glow animate-scale-in"
            data-testid="button-purchase-fab"
          >
            <Plus className="h-6 w-6" />
          </Button>
        </div>
      </div>
      
      <PurchaseModal 
        open={isPurchaseModalOpen}
        onOpenChange={handlePurchaseModalClose}
      />
    </div>
  );
}