import { Moon, Sun, Wallet } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useTheme } from "./theme-provider";
import { useQuery } from "@tanstack/react-query";
import { useTelegram } from "@/lib/telegram";
import type { User } from "@shared/schema";

export function Header() {
  const { theme, setTheme } = useTheme();
  const { user: telegramUser } = useTelegram();

  const { data: user } = useQuery<User>({
    queryKey: ["/api/users", telegramUser?.id?.toString() || "sample_user"],
    enabled: !!telegramUser?.id || true,
  });

  const toggleTheme = () => {
    setTheme(theme === "light" ? "dark" : "light");
  };

  const formatBalance = (balance: number) => {
    return `₽${(balance / 100).toFixed(2)}`;
  };

  return (
    <header className="sticky top-0 z-50 bg-white/95 dark:bg-background/95 backdrop-blur-sm border-b border-gray-200 dark:border-border">
      <div className="flex items-center justify-between p-4">
        <h1 className="text-xl font-semibold" data-testid="app-title">OnlineSim</h1>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 bg-green-50 dark:bg-green-900/20 px-3 py-1.5 rounded-lg">
            <Wallet className="h-4 w-4 text-green-600 dark:text-green-400" />
            <span 
              className="font-medium text-green-700 dark:text-green-300" 
              data-testid="user-balance"
            >
              {user ? formatBalance(user.balance) : "₽0.00"}
            </span>
          </div>
          <Button
            variant="ghost"
            size="icon"
            onClick={toggleTheme}
            className="bg-gray-100 dark:bg-secondary"
            data-testid="button-theme-toggle"
          >
            <Sun className="h-4 w-4 rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
            <Moon className="absolute h-4 w-4 rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
            <span className="sr-only">Toggle theme</span>
          </Button>
        </div>
      </div>
    </header>
  );
}
