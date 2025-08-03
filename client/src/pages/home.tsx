import { useState, useEffect } from "react";
import { Header } from "@/components/header";
import { SelectTab } from "@/components/select-tab";
import { OrdersTab } from "@/components/orders-tab";
import { MessagesTab } from "@/components/messages-tab";
import { ProfileTab } from "@/components/profile-tab";
import { BottomNavigation } from "@/components/bottom-navigation";
import { initTelegramApp } from "@/lib/telegram";

export default function Home() {
  const [bottomNavTab, setBottomNavTab] = useState("home");

  useEffect(() => {
    initTelegramApp();
  }, []);

  const handlePurchaseSuccess = () => {
    // Switch to orders tab after successful purchase
    setBottomNavTab("numbers");
  };

  const renderContent = () => {
    switch (bottomNavTab) {
      case "home":
        return <SelectTab onPurchaseSuccess={handlePurchaseSuccess} />;
      case "numbers":
        return <OrdersTab />;
      case "history":
        return <MessagesTab />;
      case "profile":
        return <ProfileTab />;
      default:
        return <SelectTab onPurchaseSuccess={handlePurchaseSuccess} />;
    }
  };

  return (
    <div className="min-h-screen bg-background flex flex-col">
      <Header />
      
      <main className="flex-1 pb-16">
        {renderContent()}
      </main>
      
      <BottomNavigation 
        activeTab={bottomNavTab}
        onTabChange={setBottomNavTab}
      />
    </div>
  );
}
