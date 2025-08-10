import { useQuery } from "@tanstack/react-query";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useCopyToClipboard } from "@/lib/copy-utils";
import { useToast } from "@/hooks/use-toast";
import type { Message, Order, Service } from "@shared/schema";

interface MessageWithDetails extends Message {
  order?: Order;
  service?: Service;
}

export function MessagesTab() {
  const { copyToClipboard, extractCode } = useCopyToClipboard();
  const { toast } = useToast();
  
  // Получаем telegramUser
  const telegramUser = window.Telegram?.WebApp?.initDataUnsafe?.user;
  const userId = telegramUser?.id?.toString() || "sample_user";

  // Получаем заказы пользователя (они уже содержат сообщения)
  const { data: orders, isLoading: ordersLoading } = useQuery<Order[]>({
    queryKey: ["/api/orders", userId],
    queryFn: async () => {
      const response = await fetch(`/api/orders?user_id=${userId}`);
      if (!response.ok) throw new Error('Failed to fetch orders');
      return response.json();
    },
  });

  const { data: services } = useQuery<Service[]>({
    queryKey: ["/api/services"],
  });

  // Извлекаем все сообщения из заказов
  const allMessages: MessageWithDetails[] = [];
  
  orders?.forEach(order => {
    if (order.messages && order.messages.length > 0) {
      order.messages.forEach(message => {
        const service = services?.find(s => s.id === order.serviceId);
        allMessages.push({
          ...message,
          order,
          service,
        });
      });
    }
  });

  // Сортируем сообщения по времени получения (новые сначала)
  const sortedMessages = allMessages.sort((a, b) => 
    new Date(b.receivedAt).getTime() - new Date(a.receivedAt).getTime()
  );

  const handleCopyCode = async (text: string) => {
    const code = extractCode(text);
    if (code) {
      const success = await copyToClipboard(code);
      if (success) {
        toast({
          title: "Код скопирован!",
          description: `Код ${code} скопирован в буфер обмена`,
        });
      } else {
        toast({
          title: "Ошибка",
          description: "Не удалось скопировать код",
          variant: "destructive",
        });
      }
    } else {
      toast({
        title: "Код не найден",
        description: "В сообщении не найден код подтверждения",
        variant: "destructive",
      });
    }
  };

  const getServiceIcon = (serviceName?: string) => {
    switch (serviceName?.toLowerCase()) {
      case "telegram":
        return "💬";
      case "whatsapp":
        return "📱";
      case "discord":
        return "🎮";
      default:
        return "📱";
    }
  };

  const getServiceColor = (serviceName?: string) => {
    switch (serviceName?.toLowerCase()) {
      case "telegram":
        return "bg-blue-100 dark:bg-blue-900/20";
      case "whatsapp":
        return "bg-green-100 dark:bg-green-900/20";
      case "discord":
        return "bg-purple-100 dark:bg-purple-900/20";
      default:
        return "bg-gray-100 dark:bg-gray-900/20";
    }
  };

  const formatTimeAgo = (date: string) => {
    const now = new Date();
    const messageTime = new Date(date);
    const diffInMinutes = Math.floor((now.getTime() - messageTime.getTime()) / (1000 * 60));
    
    if (diffInMinutes < 1) return "Только что";
    if (diffInMinutes < 60) return `${diffInMinutes} мин назад`;
    
    const diffInHours = Math.floor(diffInMinutes / 60);
    if (diffInHours < 24) return `${diffInHours}ч назад`;
    
    const diffInDays = Math.floor(diffInHours / 24);
    return `${diffInDays} дн назад`;
  };

  if (ordersLoading) {
    return (
      <div className="p-4 space-y-3">
        {[...Array(2)].map((_, i) => (
          <Card key={i} className="animate-pulse">
            <CardContent className="p-4 space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="w-8 h-8 bg-gray-200 dark:bg-gray-700 rounded-full" />
                  <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-20" />
                </div>
                <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-16" />
              </div>
              <div className="h-16 bg-gray-200 dark:bg-gray-700 rounded-lg" />
              <div className="flex items-center justify-between">
                <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-24" />
                <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-20" />
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  return (
    <div className="p-4 space-y-3">
      {sortedMessages.map((message) => (
        <Card key={message.id} data-testid={`card-message-${message.id}`}>
          <CardContent className="p-4 space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className={`w-8 h-8 rounded-full ${getServiceColor(message.service?.name)} flex items-center justify-center text-sm`}>
                  {getServiceIcon(message.service?.name)}
                </div>
                <span className="font-medium" data-testid={`text-service-${message.id}`}>
                  {message.service?.name || "Unknown"}
                </span>
              </div>
              <span className="text-sm text-gray-500 dark:text-gray-400">
                {formatTimeAgo(message.receivedAt)}
              </span>
            </div>
            
            <div className="bg-gray-50 dark:bg-background rounded-lg p-3">
              <p className="text-sm font-mono" data-testid={`text-message-${message.id}`}>
                {message.text}
              </p>
            </div>
            
            <div className="flex items-center justify-between text-sm text-gray-500 dark:text-gray-400">
              <span data-testid={`text-phone-${message.id}`}>
                {message.order?.phoneNumber}
              </span>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => handleCopyCode(message.text)}
                className="text-telegram-blue hover:text-telegram-blue/80"
                data-testid={`button-copy-code-${message.id}`}
              >
                Копировать код
              </Button>
            </div>
          </CardContent>
        </Card>
      ))}
      
      {sortedMessages.length === 0 && (
        <div className="text-center py-8 text-gray-500 dark:text-gray-400">
          Сообщений пока нет
        </div>
      )}
    </div>
  );
}