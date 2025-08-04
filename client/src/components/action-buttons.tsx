import { Button } from "@/components/ui/button";
import { BookOpen, Users, MessageCircle, ExternalLink } from "lucide-react";

interface ActionButtonsProps {
  onOpenInstructions: () => void;
  onOpenFAQ: () => void;
}

export function ActionButtons({ onOpenInstructions, onOpenFAQ }: ActionButtonsProps) {
  const handleTelegramAccountsClick = () => {
    window.open("https://t.me/telegram_accounts_bot", "_blank");
  };

  const handleSupportClick = () => {
    window.open("https://t.me/support", "_blank");
  };

  const handleChannelClick = () => {
    window.open("https://t.me/onlinesim_channel", "_blank");
  };

  return (
    <div className="p-4 pb-2 space-y-3 animate-fade-in">
      {/* Main Action Buttons */}
      <div className="grid grid-cols-2 gap-3">
        <Button
          onClick={onOpenInstructions}
          className="btn-cyber hover-glow bg-primary/10 border border-primary/20 text-primary hover:bg-primary/20 h-auto py-3 flex-col gap-1"
          data-testid="button-instructions"
        >
          <BookOpen className="h-5 w-5" />
          <span className="text-xs">Инструкции</span>
        </Button>
        
        <Button
          onClick={handleTelegramAccountsClick}
          className="btn-cyber hover-glow bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 text-blue-600 dark:text-blue-400 hover:bg-blue-100 dark:hover:bg-blue-900/30 h-auto py-3 flex-col gap-1"
          data-testid="button-telegram-accounts"
        >
          <Users className="h-5 w-5" />
          <span className="text-xs">Аккаунты ТГ</span>
        </Button>
      </div>

      {/* Support & Info Buttons */}
      <div className="grid grid-cols-2 gap-3">
        <Button
          onClick={handleSupportClick}
          className="btn-cyber hover-glow bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 text-green-600 dark:text-green-400 hover:bg-green-100 dark:hover:bg-green-900/30 h-auto py-3 flex-col gap-1"
          data-testid="button-support"
        >
          <MessageCircle className="h-5 w-5" />
          <span className="text-xs">Поддержка</span>
        </Button>
        
        <Button
          onClick={handleChannelClick}
          className="btn-cyber hover-glow bg-purple-50 dark:bg-purple-900/20 border border-purple-200 dark:border-purple-800 text-purple-600 dark:text-purple-400 hover:bg-purple-100 dark:hover:bg-purple-900/30 h-auto py-3 flex-col gap-1"
          data-testid="button-channel"
        >
          <ExternalLink className="h-5 w-5" />
          <span className="text-xs">Канал ТГ</span>
        </Button>
      </div>
    </div>
  );
}