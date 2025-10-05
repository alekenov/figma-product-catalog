import { useState } from 'react';
import imgImage7 from "figma:asset/b41712e9f9a73c76cc59bd6d3d6139fd0537c358.png";

interface TrackingStep {
  id: string;
  title: string;
  time: string;
  status: 'completed' | 'current' | 'pending';
  description?: string;
}

export function OrderTracking() {
  const [selectedPhoto, setSelectedPhoto] = useState<string | null>(null);
  const [feedback, setFeedback] = useState<'like' | 'dislike' | null>(null);
  const [feedbackText, setFeedbackText] = useState('');
  const [isSubmitted, setIsSubmitted] = useState(false);

  const trackingSteps: TrackingStep[] = [
    {
      id: '1',
      title: 'Заказ подтвержден',
      time: '12:30',
      status: 'completed',
      description: 'Ваш заказ принят в обработку'
    },
    {
      id: '2', 
      title: 'Букет готов',
      time: '13:45',
      status: 'completed',
      description: 'Флорист собрал ваш букет'
    },
    {
      id: '3',
      title: 'Передан курьеру',
      time: '14:20',
      status: 'current',
      description: 'Курьер направляется к получателю'
    },
    {
      id: '4',
      title: 'Доставлен',
      time: '15:00',
      status: 'pending',
      description: 'Ожидается доставка'
    }
  ];

  const submitFeedback = () => {
    setIsSubmitted(true);
    setFeedbackText('');
  };

  const handleFeedback = (type: 'like' | 'dislike') => {
    setFeedback(type);
    if (type === 'like') {
      setIsSubmitted(true);
    }
  };

  return (
    <div className="p-[var(--spacing-4)] bg-white rounded-[var(--radius-md)] space-y-[var(--spacing-4)]">
      <h2 className="text-[var(--text-primary)] font-medium">Статус доставки</h2>
      
      {/* Трекинг этапов */}
      <div className="space-y-[var(--spacing-4)]">
        {trackingSteps.map((step, index) => (
          <div key={step.id} className="flex gap-[var(--spacing-3)] items-start">
            <div className="flex flex-col items-center">
              <div className={`w-6 h-6 rounded-full flex items-center justify-center ${
                step.status === 'completed' 
                  ? 'bg-[var(--brand-success)] text-white' 
                  : step.status === 'current'
                    ? 'bg-[var(--brand-primary)] text-white'
                    : 'bg-[var(--neutral-200)] text-[var(--text-secondary)]'
              }`}>
                {step.status === 'completed' ? (
                  <svg width="12" height="12" viewBox="0 0 12 12" fill="currentColor">
                    <path d="M10 3L4.5 8.5L2 6" stroke="currentColor" strokeWidth="2" fill="none" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                ) : (
                  <div className="w-2 h-2 rounded-full bg-current" />
                )}
              </div>
              {index < trackingSteps.length - 1 && (
                <div className={`w-0.5 h-8 mt-2 ${
                  step.status === 'completed' ? 'bg-[var(--brand-success)]' : 'bg-[var(--neutral-200)]'
                }`} />
              )}
            </div>
            
            <div className="flex-1 space-y-1">
              <div className="flex items-center justify-between">
                <h4 className={`font-medium ${
                  step.status === 'current' ? 'text-[var(--brand-primary)]' : 'text-[var(--text-primary)]'
                }`}>
                  {step.title}
                </h4>
                <span className="text-sm text-[var(--text-secondary)]">{step.time}</span>
              </div>
              {step.description && (
                <p className="text-sm text-[var(--text-secondary)]">{step.description}</p>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Фото букета */}
      <div className="space-y-[var(--spacing-3)]">
        <h3 className="text-[var(--text-primary)] font-medium">Фото готового букета</h3>
        
        <div className="flex gap-[var(--spacing-2)]">
          <button
            onClick={() => setSelectedPhoto(imgImage7)}
            className="relative rounded-lg overflow-hidden"
          >
            <img 
              src={imgImage7}
              alt="Фото букета"
              className="w-full h-96 object-cover"
            />
          </button>
        </div>
        
        {/* Обратная связь */}
        <div className="space-y-[var(--spacing-3)]">
          <div>
            <h4 className="text-[var(--text-primary)] font-medium mb-2">Как вам букет?</h4>
            <div className="flex gap-[var(--spacing-3)]">
              <button
                onClick={() => handleFeedback('like')}
                disabled={isSubmitted}
                className={`flex items-center gap-2 px-4 py-2 rounded-[var(--radius-md)] border transition-colors ${
                  feedback === 'like'
                    ? 'bg-[var(--brand-success)]/10 border-[var(--brand-success)] text-[var(--brand-success)]'
                    : 'border-[var(--border)] text-[var(--text-secondary)] hover:bg-[var(--background-secondary)]'
                } ${isSubmitted ? 'opacity-50 cursor-not-allowed' : ''}`}
              >
                <span>👍</span>
                <span>Нравится</span>
              </button>
              
              <button
                onClick={() => handleFeedback('dislike')}
                disabled={isSubmitted}
                className={`flex items-center gap-2 px-4 py-2 rounded-[var(--radius-md)] border transition-colors ${
                  feedback === 'dislike'
                    ? 'bg-[var(--brand-error)]/10 border-[var(--brand-error)] text-[var(--brand-error)]'
                    : 'border-[var(--border)] text-[var(--text-secondary)] hover:bg-[var(--background-secondary)]'
                } ${isSubmitted ? 'opacity-50 cursor-not-allowed' : ''}`}
              >
                <span>👎</span>
                <span>Не нравится</span>
              </button>
            </div>
          </div>
        </div>
        
        {/* Форма обратной связи для дизлайка */}
        {feedback === 'dislike' && !isSubmitted && (
          <div className="p-[var(--spacing-4)] bg-[var(--background-secondary)] rounded-[var(--radius-md)] space-y-[var(--spacing-3)]">
            <div>
              <h3 className="text-[var(--text-primary)] font-medium mb-[var(--spacing-2)]">
                Что не понравилось?
              </h3>
              <p className="text-[var(--text-secondary)] text-sm">
                Расскажите, что можно улучшить. Ваш отзыв поможет нам стать лучше.
              </p>
            </div>
            
            <textarea
              value={feedbackText}
              onChange={(e) => setFeedbackText(e.target.value)}
              placeholder="Опишите проблему..."
              className="w-full p-3 border border-[var(--border)] rounded-[var(--radius-md)] text-[var(--text-primary)] bg-white resize-none min-h-[80px] focus:outline-none focus:ring-2 focus:ring-[var(--brand-primary)] focus:border-transparent"
              maxLength={200}
            />
            
            <div className="flex items-center justify-between">
              <span className="text-xs text-[var(--text-secondary)]">
                {feedbackText.length}/200 символов
              </span>
              <button
                onClick={submitFeedback}
                disabled={!feedbackText.trim()}
                className="px-4 py-2 bg-[var(--brand-primary)] text-white rounded-[var(--radius-md)] font-medium disabled:opacity-50 disabled:cursor-not-allowed hover:bg-[var(--brand-primary-dark)] transition-colors"
              >
                Отправить
              </button>
            </div>
          </div>
        )}
        
        {/* Сообщение об успешной отправке */}
        {isSubmitted && (
          <div className="p-[var(--spacing-3)] bg-[var(--brand-success)]/10 border border-[var(--brand-success)]/20 rounded-[var(--radius-md)]">
            <p className="text-[var(--brand-success)] text-sm font-medium">
              {feedback === 'like' 
                ? '✅ Спасибо за положительную оценку!' 
                : '✅ Спасибо за отзыв! Мы учтем ваши пожелания.'
              }
            </p>
          </div>
        )}
        
        <div className="pt-[var(--spacing-3)] border-t border-[var(--border)]">
          <p className="text-[var(--text-secondary)] text-sm">
            💡 Фотография поможет убедиться в качестве букета перед получением
          </p>
        </div>

        {selectedPhoto && (
          <div 
            className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4"
            onClick={() => setSelectedPhoto(null)}
          >
            <div className="relative max-w-sm w-full">
              <img 
                src={selectedPhoto}
                alt="Увеличенное фото"
                className="w-full h-auto rounded-lg"
              />
              <button 
                onClick={() => setSelectedPhoto(null)}
                className="absolute top-2 right-2 w-8 h-8 bg-black/50 text-white rounded-full flex items-center justify-center"
              >
                ×
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}