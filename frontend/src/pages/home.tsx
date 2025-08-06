import { useState, useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { Header } from "@/components/header";
import { SelectTab } from "@/components/select-tab";
import { OrdersTab } from "@/components/orders-tab";
import { MessagesTab } from "@/components/messages-tab";
import { ProfileTab } from "@/components/profile-tab";
import { FAQTab } from "@/components/faq-tab";
import { AdminTab } from "@/components/admin-tab";
import { BottomNavigation } from "@/components/bottom-navigation";
import { initTelegramApp } from "@/lib/telegram";
import { useTelegram } from "@/lib/telegram";
import type { User } from "@shared/schema";

export default function Home() {
  const [bottomNavTab, setBottomNavTab] = useState("home");
  const { user: telegramUser } = useTelegram();

  const { data: user } = useQuery<User>({
    queryKey: ["/api/users", telegramUser?.id?.toString() || "sample_user"],
    enabled: !!telegramUser?.id || true,
  });

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
        return (
          <SelectTab 
            onPurchaseSuccess={handlePurchaseSuccess} 
            onOpenFAQ={() => setBottomNavTab("faq")}
          />
        );
      case "numbers":
        return <OrdersTab />;
      case "history":
        return <MessagesTab />;
      case "profile":
        return <ProfileTab onOpenAdmin={() => setBottomNavTab("admin")} />;
      case "faq":
        return <FAQTab />;
      case "admin":
        return <AdminTab />;
      default:
        return (
          <SelectTab 
            onPurchaseSuccess={handlePurchaseSuccess} 
            onOpenFAQ={() => setBottomNavTab("faq")}
          />
        );
    }
  };

  return (
    <div className="min-h-screen bg-background flex flex-col">
      <Header />
      
      <main className="flex-1 pb-16 animate-fade-in">
        <div className="animate-fade-in-up">
          {renderContent()}
        </div>
      </main>
      
      <BottomNavigation 
        activeTab={bottomNavTab}
        onTabChange={setBottomNavTab}
      />
    </div>
  );
}
