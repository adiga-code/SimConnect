import { useState } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Settings, BarChart3, DollarSign, Users, TrendingUp, Save, AlertCircle } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { queryClient, apiRequest } from "@/lib/queryClient";
import type { Setting, Statistic } from "@shared/schema";

export function AdminTab() {
  const { toast } = useToast();
  const [settingsChanges, setSettingsChanges] = useState<Record<string, string>>({});

  // Fetch settings
  const { data: settings, isLoading: settingsLoading } = useQuery<Setting[]>({
    queryKey: ["/api/settings"],
  });

  // Fetch statistics
  const { data: statistics, isLoading: statsLoading } = useQuery<Statistic[]>({
    queryKey: ["/api/statistics"],
  });

  // Update setting mutation
  const updateSettingMutation = useMutation({
    mutationFn: async ({ key, value }: { key: string; value: string }) => {
      return apiRequest(`/api/settings/${key}`, {
        method: "PUT",
        body: { value },
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["/api/settings"] });
      toast({
        title: "Настройка обновлена",
        description: "Изменения успешно сохранены",
      });
      setSettingsChanges({});
    },
    onError: () => {
      toast({
        title: "Ошибка",
        description: "Не удалось обновить настройку",
        variant: "destructive",
      });
    },
  });

  const handleSettingChange = (key: string, value: string) => {
    setSettingsChanges(prev => ({
      ...prev,
      [key]: value
    }));
  };

  const handleSaveSetting = (key: string) => {
    const value = settingsChanges[key];
    if (value !== undefined) {
      updateSettingMutation.mutate({ key, value });
    }
  };

  const formatBalance = (balance: number) => {
    return `₽${(balance / 100).toFixed(2)}`;
  };

  const getSettingValue = (key: string, originalValue: string) => {
    return settingsChanges[key] !== undefined ? settingsChanges[key] : originalValue;
  };

  if (settingsLoading || statsLoading) {
    return (
      <div className="p-4 space-y-4">
        {[...Array(3)].map((_, i) => (
          <Card key={i} className="skeleton animate-pulse">
            <CardContent className="p-4">
              <div className="h-20 bg-muted rounded" />
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  return (
    <div className="p-4 animate-fade-in">
      <Tabs defaultValue="stats" className="space-y-4">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="stats" className="flex items-center gap-2">
            <BarChart3 className="h-4 w-4" />
            Статистика
          </TabsTrigger>
          <TabsTrigger value="settings" className="flex items-center gap-2">
            <Settings className="h-4 w-4" />
            Настройки
          </TabsTrigger>
        </TabsList>

        <TabsContent value="stats" className="space-y-4">
          {/* Statistics Overview */}
          {statistics && statistics.length > 0 && (
            <>
              <div className="grid grid-cols-2 gap-4">
                <Card className="card-hover animate-fade-in-up">
                  <CardContent className="p-4">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-full bg-green-100 dark:bg-green-900/20 flex items-center justify-center">
                        <DollarSign className="h-5 w-5 text-green-600 dark:text-green-400" />
                      </div>
                      <div>
                        <p className="text-sm text-muted-foreground">Доход сегодня</p>
                        <p className="text-lg font-bold text-green-600 dark:text-green-400">
                          {formatBalance(statistics[0]?.totalRevenue || 0)}
                        </p>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card className="card-hover animate-fade-in-up">
                  <CardContent className="p-4">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-full bg-blue-100 dark:bg-blue-900/20 flex items-center justify-center">
                        <TrendingUp className="h-5 w-5 text-blue-600 dark:text-blue-400" />
                      </div>
                      <div>
                        <p className="text-sm text-muted-foreground">Заказы сегодня</p>
                        <p className="text-lg font-bold text-blue-600 dark:text-blue-400">
                          {statistics[0]?.totalOrders || 0}
                        </p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <Card className="card-hover animate-fade-in-up">
                  <CardContent className="p-4">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-full bg-purple-100 dark:bg-purple-900/20 flex items-center justify-center">
                        <Users className="h-5 w-5 text-purple-600 dark:text-purple-400" />
                      </div>
                      <div>
                        <p className="text-sm text-muted-foreground">Новые пользователи</p>
                        <p className="text-lg font-bold text-purple-600 dark:text-purple-400">
                          {statistics[0]?.newUsers || 0}
                        </p>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card className="card-hover animate-fade-in-up">
                  <CardContent className="p-4">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-full bg-orange-100 dark:bg-orange-900/20 flex items-center justify-center">
                        <Users className="h-5 w-5 text-orange-600 dark:text-orange-400" />
                      </div>
                      <div>
                        <p className="text-sm text-muted-foreground">Активные пользователи</p>
                        <p className="text-lg font-bold text-orange-600 dark:text-orange-400">
                          {statistics[0]?.activeUsers || 0}
                        </p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>

              {/* Recent Statistics */}
              <Card className="card-hover animate-fade-in-up">
                <CardHeader>
                  <CardTitle className="text-lg">История статистики</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {statistics.slice(0, 7).map((stat, index) => (
                      <div key={stat.id} className="flex items-center justify-between py-2 border-b border-border last:border-b-0">
                        <div className="text-sm font-medium">{stat.date}</div>
                        <div className="flex items-center gap-4 text-sm text-muted-foreground">
                          <span>{stat.totalOrders} заказов</span>
                          <span className="text-green-600 dark:text-green-400">
                            {formatBalance(stat.totalRevenue)}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </>
          )}
        </TabsContent>

        <TabsContent value="settings" className="space-y-4">
          {/* Settings */}
          {settings && (
            <Card className="card-hover animate-fade-in-up">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Settings className="h-5 w-5 text-primary" />
                  Настройки системы
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {settings.map((setting) => (
                  <div key={setting.key} className="space-y-2">
                    <Label htmlFor={setting.key}>
                      {setting.description || setting.key}
                    </Label>
                    <div className="flex gap-2">
                      <Input
                        id={setting.key}
                        value={getSettingValue(setting.key, setting.value)}
                        onChange={(e) => handleSettingChange(setting.key, e.target.value)}
                        className="flex-1"
                        data-testid={`input-setting-${setting.key}`}
                      />
                      <Button
                        onClick={() => handleSaveSetting(setting.key)}
                        disabled={
                          settingsChanges[setting.key] === undefined || 
                          updateSettingMutation.isPending
                        }
                        size="sm"
                        className="bg-primary hover:bg-primary/90 btn-cyber"
                        data-testid={`button-save-${setting.key}`}
                      >
                        <Save className="h-4 w-4" />
                      </Button>
                    </div>
                    {setting.key === "commission_percent" && (
                      <p className="text-xs text-muted-foreground">
                        Комиссия в процентах (например: 5 для 5%)
                      </p>
                    )}
                  </div>
                ))}
              </CardContent>
            </Card>
          )}

          {/* Admin Warning */}
          <Card className="bg-amber-50 dark:bg-amber-900/10 border-amber-200 dark:border-amber-800">
            <CardContent className="p-4">
              <div className="flex items-start gap-3">
                <AlertCircle className="h-5 w-5 text-amber-600 dark:text-amber-400 mt-0.5" />
                <div>
                  <h4 className="font-medium text-amber-800 dark:text-amber-200 mb-1">
                    Административная панель
                  </h4>
                  <p className="text-sm text-amber-700 dark:text-amber-300">
                    Будьте осторожны при изменении настроек. Изменения применяются немедленно 
                    и могут повлиять на работу всего сервиса.
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}