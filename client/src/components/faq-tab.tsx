import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { ExternalLink, MessageCircle, Users, BookOpen } from "lucide-react";

interface FAQItem {
  question: string;
  answer: string;
}

const faqData: FAQItem[] = [
  {
    question: "Как получить номер телефона?",
    answer: "Выберите страну и сервис, после чего нажмите кнопку покупки. Номер будет автоматически выделен для вас на 15 минут."
  },
  {
    question: "Сколько времени действует номер?",
    answer: "Стандартное время действия номера - 15 минут. Если SMS не придет в течение этого времени, деньги будут возвращены."
  },
  {
    question: "Что делать, если SMS не пришло?",
    answer: "Если SMS не пришло в течение 15 минут, деньги автоматически возвращаются на баланс. Можете попробовать заказать другой номер."
  },
  {
    question: "Как пополнить баланс?",
    answer: "Перейдите во вкладку 'Профиль' и нажмите кнопку 'Пополнить баланс'. Доступны различные способы оплаты."
  },
  {
    question: "Можно ли использовать один номер для нескольких сервисов?",
    answer: "Нет, каждый номер предназначен только для одного сервиса. Для разных сервисов нужно заказывать отдельные номера."
  },
  {
    question: "Безопасно ли использовать ваш сервис?",
    answer: "Да, все номера виртуальные и используются только для получения SMS-кодов. Мы не сохраняем персональные данные."
  }
];

export function FAQTab() {
  const handleSupportClick = () => {
    window.open("https://t.me/support", "_blank");
  };

  const handleChannelClick = () => {
    window.open("https://t.me/onlinesim_channel", "_blank");
  };

  return (
    <div className="p-4 space-y-4 animate-fade-in">
      {/* Support Links */}
      <div className="grid grid-cols-2 gap-3 mb-6">
        <Button
          onClick={handleSupportClick}
          className="btn-cyber hover-glow bg-primary/10 border border-primary/20 text-primary hover:bg-primary/20"
          data-testid="button-support"
        >
          <MessageCircle className="h-4 w-4 mr-2" />
          Техподдержка
        </Button>
        
        <Button
          onClick={handleChannelClick}
          className="btn-cyber hover-glow bg-primary/10 border border-primary/20 text-primary hover:bg-primary/20"
          data-testid="button-channel"
        >
          <Users className="h-4 w-4 mr-2" />
          Канал Telegram
        </Button>
      </div>

      {/* FAQ Section */}
      <Card className="card-hover animate-fade-in-up">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BookOpen className="h-5 w-5 text-primary" />
            Часто задаваемые вопросы
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {faqData.map((faq, index) => (
            <div 
              key={index} 
              className="border-b border-border pb-4 last:border-b-0 last:pb-0 animate-fade-in-up"
              style={{ animationDelay: `${index * 0.1}s` }}
            >
              <h3 
                className="font-medium text-foreground mb-2" 
                data-testid={`faq-question-${index}`}
              >
                {faq.question}
              </h3>
              <p 
                className="text-sm text-muted-foreground leading-relaxed" 
                data-testid={`faq-answer-${index}`}
              >
                {faq.answer}
              </p>
            </div>
          ))}
        </CardContent>
      </Card>

      {/* Additional Info */}
      <Card className="card-hover animate-fade-in-up bg-primary/5 border-primary/20">
        <CardContent className="p-4">
          <div className="flex items-start gap-3">
            <MessageCircle className="h-5 w-5 text-primary mt-0.5" />
            <div>
              <h4 className="font-medium text-primary mb-1">Нужна помощь?</h4>
              <p className="text-sm text-muted-foreground mb-3">
                Если не нашли ответ на свой вопрос, обратитесь в техподдержку.
              </p>
              <Button 
                onClick={handleSupportClick}
                size="sm"
                className="bg-primary hover:bg-primary/90 btn-cyber"
                data-testid="button-contact-support"
              >
                <ExternalLink className="h-3 w-3 mr-1" />
                Связаться с поддержкой
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}