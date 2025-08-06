import { Search } from "lucide-react";
import { Input } from "@/components/ui/input";

interface SearchBarProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
}

export function SearchBar({ value, onChange, placeholder = "Поиск стран или сервисов..." }: SearchBarProps) {
  return (
    <div className="p-4 bg-muted/30">
      <div className="relative">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        <Input
          type="text"
          placeholder={placeholder}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          className="pl-10 bg-background border-border focus:ring-2 focus:ring-primary"
          data-testid="input-search"
        />
      </div>
    </div>
  );
}
