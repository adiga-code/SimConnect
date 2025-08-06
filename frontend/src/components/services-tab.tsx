import { useQuery } from "@tanstack/react-query";
import { Card, CardContent } from "@/components/ui/card";
import { ChevronRight } from "lucide-react";
import type { Service } from "@shared/schema";

interface ServicesTabProps {
  searchQuery: string;
  onServiceSelect: (service: Service) => void;
}

export function ServicesTab({ searchQuery, onServiceSelect }: ServicesTabProps) {
  const { data: services, isLoading } = useQuery<Service[]>({
    queryKey: ["/api/services"],
  });

  const filteredServices = services?.filter(service =>
    service.name.toLowerCase().includes(searchQuery.toLowerCase())
  ) || [];

  const getServiceIcon = (iconClass: string) => {
    const iconMap: Record<string, string> = {
      "fab fa-telegram": "💬",
      "fab fa-whatsapp": "📱",
      "fab fa-discord": "🎮",
    };
    return iconMap[iconClass] || "📱";
  };

  const getServiceColor = (name: string) => {
    switch (name.toLowerCase()) {
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

  if (isLoading) {
    return (
      <div className="p-4 space-y-3">
        {[...Array(3)].map((_, i) => (
          <Card key={i} className="skeleton animate-pulse">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-muted rounded-xl" />
                  <div className="space-y-2">
                    <div className="h-4 bg-muted rounded w-20" />
                    <div className="h-3 bg-muted rounded w-16" />
                  </div>
                </div>
                <div className="w-4 h-4 bg-muted rounded" />
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  return (
    <div className="p-4 space-y-3">
      {filteredServices.map((service) => (
        <Card
          key={service.id}
          className="card-hover cursor-pointer animate-fade-in-up"
          onClick={() => onServiceSelect(service)}
          data-testid={`card-service-${service.id}`}
        >
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className={`w-10 h-10 rounded-xl ${getServiceColor(service.name)} flex items-center justify-center text-lg`}>
                  {getServiceIcon(service.icon)}
                </div>
                <div>
                  <h3 className="font-medium" data-testid={`text-service-name-${service.id}`}>
                    {service.name}
                  </h3>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    ₽{service.priceFrom} - ₽{service.priceTo}
                  </p>
                </div>
              </div>
              <ChevronRight className="h-4 w-4 text-gray-400" />
            </div>
          </CardContent>
        </Card>
      ))}
      {filteredServices.length === 0 && (
        <div className="text-center py-8 text-gray-500 dark:text-gray-400">
          Сервисы не найдены
        </div>
      )}
    </div>
  );
}
