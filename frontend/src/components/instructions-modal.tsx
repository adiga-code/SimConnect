import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Phone, Clock, CreditCard, MessageSquare, CheckCircle, HelpCircle } from "lucide-react";

interface InstructionsModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onOpenFAQ?: () => void;
}

export function InstructionsModal({ open, onOpenChange, onOpenFAQ }: InstructionsModalProps) {
  const steps = [
    {
      icon: CreditCard,
      title: "Пополните баланс",
      description: "Убедитесь, что на вашем балансе достаточно средств для покупки номера"
    },
    {
      icon: Phone,
      title: "Выберите страну и сервис",
      description: "Выберите нужную страну и сервис, для которого нужен номер телефона"
    },
    {
      icon: MessageSquare,
      title: "Получите номер",
      description: "После оплаты вы получите номер телефона для регистрации"
    },
    {
      icon: Clock,
      title: "Дождитесь SMS",
      description: "У вас есть 15 минут, чтобы получить SMS с кодом подтверждения"
    },
    {
      icon: CheckCircle,
      title: "Завершите регистрацию",
      description: "Используйте полученный код для завершения регистрации в сервисе"
    }
  ];

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-md animate-scale-in">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Phone className="h-5 w-5 text-primary" />
            Как использовать номера
          </DialogTitle>
        </DialogHeader>
        
        <div className="space-y-4">
          {steps.map((step, index) => {
            const Icon = step.icon;
            return (
              <Card 
                key={index} 
                className="card-hover animate-fade-in-up"
                style={{ animationDelay: `${index * 0.1}s` }}
              >
                <CardContent className="p-3">
                  <div className="flex items-start gap-3">
                    <div className="w-8 h-8 rounded-full bg-primary/10 border border-primary/20 flex items-center justify-center mt-0.5">
                      <Icon className="h-4 w-4 text-primary" />
                    </div>
                    <div className="flex-1">
                      <h4 className="font-medium text-foreground mb-1">
                        {index + 1}. {step.title}
                      </h4>
                      <p className="text-sm text-muted-foreground">
                        {step.description}
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>

        <div className="flex gap-2 pt-4">
          <Button
            onClick={() => onOpenChange(false)}
            variant="outline"
            className="flex-1"
            data-testid="button-close-instructions"
          >
            Понятно
          </Button>
          {onOpenFAQ && (
            <Button
              onClick={() => {
                onOpenChange(false);
                onOpenFAQ();
              }}
              className="flex-1 bg-primary hover:bg-primary/90 btn-cyber"
              data-testid="button-open-faq"
            >
              <HelpCircle className="h-4 w-4 mr-2" />
              FAQ
            </Button>
          )}
        </div>

        <Card className="bg-primary/5 border-primary/20 mt-4">
          <CardContent className="p-3">
            <div className="flex items-center gap-2 mb-2">
              <Clock className="h-4 w-4 text-primary" />
              <span className="font-medium text-primary text-sm">Важно помнить</span>
            </div>
            <p className="text-xs text-muted-foreground">
              Время действия номера составляет 15 минут. Если SMS не придет в течение этого времени, 
              деньги автоматически вернутся на ваш баланс.
            </p>
          </CardContent>
        </Card>
      </DialogContent>
    </Dialog>
  );
}