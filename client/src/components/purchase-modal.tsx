import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Card, CardContent } from "@/components/ui/card";
import { useToast } from "@/hooks/use-toast";
import { useTelegram } from "@/lib/telegram";
import { apiRequest } from "@/lib/queryClient";
import type { Country, Service, Order } from "@shared/schema";

interface PurchaseModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function PurchaseModal({ open, onOpenChange }: PurchaseModalProps) {
  const [selectedCountryId, setSelectedCountryId] = useState<string>("");
  const [selectedServiceId, setSelectedServiceId] = useState<string>("");
  const { toast } = useToast();
  const { user: telegramUser } = useTelegram();
  const queryClient = useQueryClient();

  const { data: countries } = useQuery<Country[]>({
    queryKey: ["/api/countries"],
  });

  const { data: services } = useQuery<Service[]>({
    queryKey: ["/api/services"],
  });

  const selectedCountry = countries?.find(c => c.id === selectedCountryId);
  const selectedService = services?.find(s => s.id === selectedServiceId);

  const calculatePrice = () => {
    if (!selectedCountry || !selectedService) return 0;
    return Math.max(selectedCountry.priceFrom, selectedService.priceFrom);
  };

  const generatePhoneNumber = (countryCode: string) => {
    const numbers = Math.random().toString().slice(2, 9);
    switch (countryCode) {
      case "RU":
        return `+7 916 ${numbers.slice(0, 3)}-${numbers.slice(3, 5)}-${numbers.slice(5, 7)}`;
      case "UA":
        return `+380 ${numbers.slice(0, 2)} ${numbers.slice(2, 5)}-${numbers.slice(5, 7)}-${numbers.slice(7, 9)}`;
      case "KZ":
        return `+7 ${numbers.slice(0, 3)} ${numbers.slice(3, 6)}-${numbers.slice(6, 8)}-${numbers.slice(8, 10)}`;
      case "US":
        return `+1 ${numbers.slice(0, 3)} ${numbers.slice(3, 6)}-${numbers.slice(6, 10)}`;
      default:
        return `+${numbers}`;
    }
  };

  const purchaseMutation = useMutation({
    mutationFn: async () => {
      if (!selectedCountryId || !selectedServiceId) {
        throw new Error("Выберите страну и сервис");
      }

      const phoneNumber = generatePhoneNumber(selectedCountry?.code || "");
      const price = calculatePrice();
      const expiresAt = new Date(Date.now() + 20 * 60 * 1000); // 20 minutes

      const response = await apiRequest("POST", "/api/orders", {
        telegramId: telegramUser?.id?.toString() || "sample_user",
        phoneNumber,
        countryId: selectedCountryId,
        serviceId: selectedServiceId,
        price,
        status: "active",
        expiresAt: expiresAt.toISOString(),
      });

      return response.json();
    },
    onSuccess: (order: Order) => {
      queryClient.invalidateQueries({ queryKey: ["/api/orders"] });
      queryClient.invalidateQueries({ queryKey: ["/api/users"] });
      
      toast({
        title: "Номер успешно приобретен!",
        description: `Номер ${order.phoneNumber} готов к использованию`,
      });
      
      onOpenChange(false);
      setSelectedCountryId("");
      setSelectedServiceId("");
    },
    onError: (error: any) => {
      toast({
        title: "Ошибка покупки",
        description: error.message || "Не удалось приобрести номер",
        variant: "destructive",
      });
    },
  });

  const handlePurchase = () => {
    purchaseMutation.mutate();
  };

  const availableCountries = countries?.filter(c => c.available) || [];

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle data-testid="title-purchase-modal">Покупка номера</DialogTitle>
        </DialogHeader>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">Страна</label>
            <Select value={selectedCountryId} onValueChange={setSelectedCountryId}>
              <SelectTrigger data-testid="select-country">
                <SelectValue placeholder="Выберите страну" />
              </SelectTrigger>
              <SelectContent>
                {availableCountries.map((country) => (
                  <SelectItem key={country.id} value={country.id}>
                    {country.flag} {country.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-2">Сервис</label>
            <Select value={selectedServiceId} onValueChange={setSelectedServiceId}>
              <SelectTrigger data-testid="select-service">
                <SelectValue placeholder="Выберите сервис" />
              </SelectTrigger>
              <SelectContent>
                {services?.map((service) => (
                  <SelectItem key={service.id} value={service.id}>
                    {service.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          
          <Card className="bg-blue-50 dark:bg-blue-900/20">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <span className="font-medium">Стоимость:</span>
                <span className="text-xl font-bold text-telegram-blue" data-testid="text-price">
                  ₽{calculatePrice()}
                </span>
              </div>
            </CardContent>
          </Card>
          
          <Button
            onClick={handlePurchase}
            disabled={!selectedCountryId || !selectedServiceId || purchaseMutation.isPending}
            className="w-full bg-telegram-blue hover:bg-telegram-blue/90"
            data-testid="button-purchase"
          >
            {purchaseMutation.isPending ? "Покупка..." : "Купить номер"}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
