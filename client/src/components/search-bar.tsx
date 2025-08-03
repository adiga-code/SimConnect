import { Search } from "lucide-react";
import { Input } from "@/components/ui/input";

interface SearchBarProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
}

export function SearchBar({ value, onChange, placeholder = "Поиск стран или сервисов..." }: SearchBarProps) {
  return (
    <div className="p-4 bg-gray-50 dark:bg-secondary/50">
      <div className="relative">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
        <Input
          type="text"
          placeholder={placeholder}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          className="pl-10 bg-white dark:bg-secondary border-gray-200 dark:border-secondary focus:ring-2 focus:ring-telegram-blue"
          data-testid="input-search"
        />
      </div>
    </div>
  );
}
