import { useQuery } from "@tanstack/react-query";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Copy } from "lucide-react";
import { useCopyToClipboard } from "@/lib/copy-utils";
import { useToast } from "@/hooks/use-toast";
import type { Order, Country, Service } from "@shared/schema";

interface OrderWithDetails extends Order {
  country?: Country;
  service?: Service;
}

export function OrdersTab() {
  const { copyToClipboard } = useCopyToClipboard();
  const { toast } = useToast();

  const { data: orders, isLoading } = useQuery<Order[]>({
    queryKey: ["/api/orders"],
  });

  const { data: countries } = useQuery<Country[]>({
    queryKey: ["/api/countries"],
  });

  const { data: services } = useQuery<Service[]>({
    queryKey: ["/api/services"],
  });

  const ordersWithDetails: OrderWithDetails[] = orders?.map(order => ({
    ...order,
    country: countries?.find(c => c.id === order.countryId),
    service: services?.find(s => s.id === order.serviceId),
  })) || [];

  const handleCopyNumber = async (phoneNumber: string) => {
    const success = await copyToClipboard(phoneNumber);
    if (success) {
      toast({
        title: "Скопировано!",
        description: "Номер телефона скопирован в буфер обмена",
      });
    } else {
      toast({
        title: "Ошибка",
        description: "Не удалось скопировать номер",
        variant: "destructive",
      });
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "active":
        return (
          <Badge variant="secondary" className="bg-green-100 dark:bg-green-900/20 text-green-700 dark:text-green-300">
            Активен
          </Badge>
        );
      case "completed":
        return (
          <Badge variant="secondary" className="bg-blue-100 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300">
            Завершен
          </Badge>
        );
      case "expired":
        return (
          <Badge variant="secondary" className="bg-red-100 dark:bg-red-900/20 text-red-700 dark:text-red-300">
            Истек
          </Badge>
        );
      default:
        return null;
    }
  };

  const getTimeRemaining = (expiresAt: string) => {
    const now = new Date();
    const expiry = new Date(expiresAt);
    const diff = expiry.getTime() - now.getTime();
    
    if (diff <= 0) return "Истек";
    
    const minutes = Math.floor(diff / (1000 * 60));
    const hours = Math.floor(minutes / 60);
    
    if (hours > 0) {
      return `Истекает через ${hours}ч ${minutes % 60}м`;
    }
    return `Истекает через ${minutes} мин`;
  };

  if (isLoading) {
    return (
      <div className="p-4 space-y-3">
        {[...Array(2)].map((_, i) => (
          <Card key={i} className="animate-pulse">
            <CardContent className="p-4 space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-16" />
                  <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-12" />
                </div>
                <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-8" />
              </div>
              <div className="flex items-center justify-between">
                <div className="h-6 bg-gray-200 dark:bg-gray-700 rounded w-32" />
                <div className="w-8 h-8 bg-gray-200 dark:bg-gray-700 rounded-lg" />
              </div>
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
      {ordersWithDetails.map((order) => (
        <Card key={order.id} data-testid={`card-order-${order.id}`}>
          <CardContent className="p-4 space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                {getStatusBadge(order.status)}
                <span className="text-sm text-gray-500 dark:text-gray-400">
                  #{order.id.slice(-5)}
                </span>
              </div>
              <span className="text-sm font-medium">₽{order.price}</span>
            </div>
            
            <div className="flex items-center justify-between">
              <span 
                className="font-mono text-lg font-medium" 
                data-testid={`text-phone-${order.id}`}
              >
                {order.phoneNumber}
              </span>
              <Button
                variant="ghost"
                size="icon"
                onClick={() => handleCopyNumber(order.phoneNumber)}
                className="bg-gray-100 dark:bg-background"
                data-testid={`button-copy-${order.id}`}
              >
                <Copy className="h-4 w-4" />
              </Button>
            </div>
            
            <div className="flex items-center justify-between text-sm text-gray-500 dark:text-gray-400">
              <span>
                {order.service?.name} • {order.country?.name}
              </span>
              <span>
                {order.status === "active" ? getTimeRemaining(order.expiresAt) : "Получен код"}
              </span>
            </div>
          </CardContent>
        </Card>
      ))}
      
      {ordersWithDetails.length === 0 && (
        <div className="text-center py-8 text-gray-500 dark:text-gray-400">
          У вас пока нет заказов
        </div>
      )}
    </div>
  );
}
