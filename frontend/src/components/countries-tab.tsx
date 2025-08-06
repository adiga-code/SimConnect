import { useQuery } from "@tanstack/react-query";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import type { Country } from "@shared/schema";

interface CountriesTabProps {
  searchQuery: string;
  onCountrySelect: (country: Country) => void;
}

export function CountriesTab({ searchQuery, onCountrySelect }: CountriesTabProps) {
  const { data: countries, isLoading } = useQuery<Country[]>({
    queryKey: ["/api/countries"],
  });

  const filteredCountries = countries?.filter(country =>
    country.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    country.code.toLowerCase().includes(searchQuery.toLowerCase())
  ) || [];

  const getStatusBadge = (status: string, numbersCount: number) => {
    switch (status) {
      case "available":
        return (
          <Badge variant="secondary" className="bg-green-100 dark:bg-green-900/20 text-green-700 dark:text-green-300">
            Доступно
          </Badge>
        );
      case "low":
        return (
          <Badge variant="secondary" className="bg-yellow-100 dark:bg-yellow-900/20 text-yellow-700 dark:text-yellow-300">
            Мало номеров
          </Badge>
        );
      case "unavailable":
        return (
          <Badge variant="secondary" className="bg-red-100 dark:bg-red-900/20 text-red-700 dark:text-red-300">
            Недоступно
          </Badge>
        );
      default:
        return null;
    }
  };

  if (isLoading) {
    return (
      <div className="p-4 space-y-3">
        {[...Array(4)].map((_, i) => (
          <Card key={i} className="animate-pulse">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 bg-gray-200 dark:bg-gray-700 rounded-full" />
                  <div className="space-y-2">
                    <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-20" />
                    <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-16" />
                  </div>
                </div>
                <div className="space-y-2">
                  <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-16" />
                  <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-20" />
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  return (
    <div className="p-4 space-y-3">
      {filteredCountries.map((country) => (
        <Card
          key={country.id}
          className={cn(
            "card-hover cursor-pointer animate-fade-in-up",
            !country.available && "opacity-50 cursor-not-allowed"
          )}
          onClick={() => country.available && onCountrySelect(country)}
          data-testid={`card-country-${country.id}`}
        >
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-400 to-blue-600 flex items-center justify-center text-white font-semibold text-sm">
                  {country.flag}
                </div>
                <div>
                  <h3 className="font-medium" data-testid={`text-country-name-${country.id}`}>
                    {country.name}
                  </h3>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    от ₽{country.priceFrom}
                  </p>
                </div>
              </div>
              <div className="text-right">
                {getStatusBadge(country.status, country.numbersCount)}
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                  {country.numbersCount} {country.numbersCount === 1 ? 'номер' : 'номеров'}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      ))}
      {filteredCountries.length === 0 && (
        <div className="text-center py-8 text-gray-500 dark:text-gray-400">
          Страны не найдены
        </div>
      )}
    </div>
  );
}

function cn(...classes: (string | undefined)[]) {
  return classes.filter(Boolean).join(" ");
}
