import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Wallet, Gift, Users, CreditCard, Copy } from "lucide-react";
import { useTelegram } from "@/lib/telegram";
import { useCopyToClipboard } from "@/lib/copy-utils";
import { useToast } from "@/hooks/use-toast";
import type { User } from "@shared/schema";

export function ProfileTab() {
  const [promoCode, setPromoCode] = useState("");
  const [refLink] = useState("https://t.me/onlinesim_bot?start=ref123456");
  const { user: telegramUser } = useTelegram();
  const { copyToClipboard } = useCopyToClipboard();
  const { toast } = useToast();

  const { data: user } = useQuery<User>({
    queryKey: ["/api/users", telegramUser?.id?.toString() || "sample_user"],
    enabled: !!telegramUser?.id || true,
  });

  const formatBalance = (balance: number) => {
    return `₽${(balance / 100).toFixed(2)}`;
  };

  const handleCopyRefLink = async () => {
    const success = await copyToClipboard(refLink);
    if (success) {
      toast({
        title: "Скопировано!",
        description: "Реферальная ссылка скопирована в буфер обмена",
      });
    } else {
      toast({
        title: "Ошибка",
        description: "Не удалось скопировать ссылку",
        variant: "destructive",
      });
    }
  };

  const handleTopUp = () => {
    toast({
      title: "Пополнение баланса",
      description: "Функция пополнения будет добавлена позже",
    });
  };

  const handleActivatePromo = () => {
    if (!promoCode.trim()) {
      toast({
        title: "Ошибка",
        description: "Введите промокод",
        variant: "destructive",
      });
      return;
    }

    toast({
      title: "Промокод активирован",
      description: `Промокод ${promoCode} успешно активирован!`,
    });
    setPromoCode("");
  };

  return (
    <div className="p-4 space-y-4">
      {/* User Info */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Wallet className="h-5 w-5" />
            Мой профиль
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-500 dark:text-gray-400">Пользователь:</span>
            <span className="font-medium" data-testid="text-username">
              {user?.username || telegramUser?.username || "Пользователь"}
            </span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-500 dark:text-gray-400">Баланс:</span>
            <span className="text-xl font-bold text-green-600 dark:text-green-400" data-testid="text-user-balance">
              {user ? formatBalance(user.balance) : "₽0.00"}
            </span>
          </div>
          <Button 
            onClick={handleTopUp}
            className="w-full bg-primary hover:bg-primary/90 shadow-cyber btn-cyber hover-glow"
            data-testid="button-top-up"
          >
            <CreditCard className="h-4 w-4 mr-2" />
            Пополнить баланс
          </Button>
        </CardContent>
      </Card>

      {/* Promo Code */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Gift className="h-5 w-5" />
            Промокод
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex gap-2">
            <Input
              placeholder="Введите промокод"
              value={promoCode}
              onChange={(e) => setPromoCode(e.target.value)}
              data-testid="input-promo-code"
            />
            <Button 
              onClick={handleActivatePromo}
              variant="outline"
              data-testid="button-activate-promo"
            >
              Активировать
            </Button>
          </div>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Введите промокод для получения бонусов
          </p>
        </CardContent>
      </Card>

      {/* Referral Program */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Users className="h-5 w-5" />
            Реферальная программа
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="bg-primary/5 border border-primary/20 p-3 rounded-lg">
            <h4 className="font-medium text-primary mb-2">Приглашайте друзей!</h4>
            <p className="text-sm text-muted-foreground">
              Получайте 10% с каждой покупки приглашенных пользователей
            </p>
          </div>
          
          <div className="space-y-2">
            <label className="text-sm font-medium">Ваша реферальная ссылка:</label>
            <div className="flex gap-2">
              <Input
                value={refLink}
                readOnly
                className="bg-gray-50 dark:bg-secondary"
                data-testid="input-ref-link"
              />
              <Button
                variant="outline"
                size="icon"
                onClick={handleCopyRefLink}
                data-testid="button-copy-ref-link"
              >
                <Copy className="h-4 w-4" />
              </Button>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4 pt-2">
            <div className="text-center">
              <div className="text-2xl font-bold text-primary">0</div>
              <div className="text-sm text-muted-foreground">Приглашено</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-primary">₽0.00</div>
              <div className="text-sm text-muted-foreground">Заработано</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Statistics */}
      <Card>
        <CardHeader>
          <CardTitle>Статистика</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-4">
            <div className="text-center p-3 bg-gray-50 dark:bg-secondary rounded-lg">
              <div className="text-xl font-bold">2</div>
              <div className="text-sm text-gray-500 dark:text-gray-400">Всего заказов</div>
            </div>
            <div className="text-center p-3 bg-gray-50 dark:bg-secondary rounded-lg">
              <div className="text-xl font-bold">₽33</div>
              <div className="text-sm text-gray-500 dark:text-gray-400">Потрачено</div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}