import { useState, useEffect } from "react";
import { Plus } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Header } from "@/components/header";
import { SearchBar } from "@/components/search-bar";
import { TabNavigation } from "@/components/tab-navigation";
import { CountriesTab } from "@/components/countries-tab";
import { ServicesTab } from "@/components/services-tab";
import { OrdersTab } from "@/components/orders-tab";
import { MessagesTab } from "@/components/messages-tab";
import { PurchaseModal } from "@/components/purchase-modal";
import { BottomNavigation } from "@/components/bottom-navigation";
import { initTelegramApp } from "@/lib/telegram";
import type { Country, Service } from "@shared/schema";

const tabs = [
  { id: "countries", label: "Страны" },
  { id: "services", label: "Сервисы" },
  { id: "orders", label: "Заказы" },
  { id: "messages", label: "SMS" },
];

export default function Home() {
  const [activeTab, setActiveTab] = useState("countries");
  const [bottomNavTab, setBottomNavTab] = useState("home");
  const [searchQuery, setSearchQuery] = useState("");
  const [isPurchaseModalOpen, setIsPurchaseModalOpen] = useState(false);

  useEffect(() => {
    initTelegramApp();
  }, []);

  const handleCountrySelect = (country: Country) => {
    console.log("Selected country:", country);
    setIsPurchaseModalOpen(true);
  };

  const handleServiceSelect = (service: Service) => {
    console.log("Selected service:", service);
    setIsPurchaseModalOpen(true);
  };

  const handleBottomNavChange = (tab: string) => {
    setBottomNavTab(tab);
    
    // Map bottom navigation to corresponding content
    switch (tab) {
      case "home":
        setActiveTab("countries");
        break;
      case "numbers":
        setActiveTab("orders");
        break;
      case "history":
        setActiveTab("messages");
        break;
      case "profile":
        setActiveTab("services");
        break;
    }
  };

  const handleTopTabChange = (tab: string) => {
    setActiveTab(tab);
    
    // Update bottom navigation to match
    switch (tab) {
      case "countries":
        setBottomNavTab("home");
        break;
      case "orders":
        setBottomNavTab("numbers");
        break;
      case "messages":
        setBottomNavTab("history");
        break;
      case "services":
        setBottomNavTab("profile");
        break;
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
      case "orders":
        return <OrdersTab />;
      case "messages":
        return <MessagesTab />;
      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <Header />
      
      <SearchBar 
        value={searchQuery}
        onChange={setSearchQuery}
        placeholder="Поиск стран или сервисов..."
      />
      
      <TabNavigation 
        tabs={tabs}
        activeTab={activeTab}
        onTabChange={handleTopTabChange}
      />
      
      <main className="pb-20">
        {renderTabContent()}
      </main>
      
      {/* Floating Action Button */}
      <div className="fixed bottom-20 right-4 z-40">
        <Button
          size="icon"
          onClick={() => setIsPurchaseModalOpen(true)}
          className="w-14 h-14 bg-telegram-blue hover:bg-telegram-blue/90 text-white rounded-full shadow-lg"
          data-testid="button-purchase-fab"
        >
          <Plus className="h-6 w-6" />
        </Button>
      </div>
      
      <BottomNavigation 
        activeTab={bottomNavTab}
        onTabChange={handleBottomNavChange}
      />
      
      <PurchaseModal 
        open={isPurchaseModalOpen}
        onOpenChange={setIsPurchaseModalOpen}
      />
    </div>
  );
}
