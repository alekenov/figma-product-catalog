import { CvetyTextarea } from './ui/cvety-textarea';
import { useState } from 'react';

export function CardAddOn() {
  const [isExpanded, setIsExpanded] = useState(false);
  const [cardText, setCardText] = useState('');
  const [hasCard, setHasCard] = useState(false);
  const maxLength = 200;

  const handleAddCard = () => {
    if (cardText.trim()) {
      setHasCard(true);
      setIsExpanded(false);
    }
  };

  const handleCancel = () => {
    if (!hasCard) {
      setCardText('');
    }
    setIsExpanded(false);
  };

  const handleEdit = () => {
    setIsExpanded(true);
  };

  const handleRemove = () => {
    setCardText('');
    setHasCard(false);
    setIsExpanded(false);
  };

  return (
    <div className="flex flex-col gap-[var(--spacing-4)] w-full">
      <div 
        className="p-[var(--spacing-4)] bg-white rounded-[var(--radius-md)]"
        onClick={!isExpanded && !hasCard ? () => setIsExpanded(true) : undefined}
        style={{ cursor: !isExpanded && !hasCard ? 'pointer' : 'default' }}
      >
        {!isExpanded && !hasCard && (
          <div className="flex items-center gap-[var(--spacing-3)] w-full">
            <div className="w-6 h-6 border border-[var(--text-secondary)] rounded-full flex items-center justify-center">
              <svg className="w-4 h-4 text-[var(--text-secondary)]" viewBox="0 0 24 24" fill="none">
                <path d="M12 8V16M8 12H16" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </div>
            <p className="text-body text-[var(--text-secondary)]">Добавить открытку (бесплатно)</p>
          </div>
        )}

        {!isExpanded && hasCard && (
          <div className="space-y-[var(--spacing-3)]">
            <div className="flex items-center gap-[var(--spacing-3)]">
              <div className="w-6 h-6 bg-[var(--brand-primary)] rounded-full flex items-center justify-center">
                <svg className="w-4 h-4 text-white" viewBox="0 0 24 24" fill="none">
                  <path d="M20 6L9 17L4 12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </div>
              <p className="text-body-emphasis text-[var(--text-primary)]">Открытка добавлена</p>
            </div>
            <div className="bg-[var(--background-secondary)] rounded-lg p-[var(--spacing-3)] ml-9">
              <p className="text-caption text-[var(--text-secondary)]">"{cardText}"</p>
            </div>
            <div className="flex gap-[var(--spacing-2)] ml-9">
              <button
                type="button"
                onClick={handleEdit}
                className="px-4 py-2 rounded-2xl transition-all text-label border bg-white text-[var(--text-secondary)] border-[var(--border)] flex-shrink-0"
              >
                Изменить
              </button>
              <button
                type="button"
                onClick={handleRemove}
                className="px-4 py-2 rounded-2xl transition-all text-label border bg-white text-[var(--text-secondary)] border-[var(--border)] flex-shrink-0"
              >
                Удалить
              </button>
            </div>
          </div>
        )}

        {isExpanded && (
          <div className="space-y-[var(--spacing-4)]">
            <div className="flex items-center gap-[var(--spacing-3)]">
              <div className="w-6 h-6 bg-[var(--brand-primary)] rounded-full flex items-center justify-center">
                <svg className="w-4 h-4 text-white" viewBox="0 0 24 24" fill="none">
                  <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </div>
              <p className="text-body-emphasis text-[var(--text-primary)]">Текст для открытки</p>
            </div>
            
            <div className="space-y-[var(--spacing-2)]">
              <CvetyTextarea
                value={cardText}
                onChange={(e) => setCardText(e.target.value)}
                placeholder="Например: Дорогая мама, поздравляю с днем рождения! Желаю здоровья, счастья и много радостных моментов!"
                maxLength={maxLength}
                className="min-h-[80px]"
              />
              <div className="flex justify-between items-center">
                <p className="text-caption text-[var(--text-secondary)]">
                  Максимум {maxLength} символов
                </p>
                <p className={`text-caption ${cardText.length > maxLength * 0.9 ? 'text-[var(--brand-warning)]' : 'text-[var(--text-secondary)]'}`}>
                  {cardText.length}/{maxLength}
                </p>
              </div>
            </div>

            <div className="flex gap-[var(--spacing-2)]">
              <button
                type="button"
                onClick={handleAddCard}
                disabled={!cardText.trim() || cardText.length > maxLength}
                className={`relative px-4 py-2 rounded-2xl transition-all text-label border flex-shrink-0 ${
                  !cardText.trim() || cardText.length > maxLength
                    ? 'bg-white text-[var(--text-muted)] border-[var(--border)] cursor-not-allowed'
                    : 'bg-white text-[var(--text-primary)] border-[var(--border)]'
                }`}
              >
                {hasCard ? 'Сохранить' : 'Добавить'}
                {!(!cardText.trim() || cardText.length > maxLength) && (
                  <div className="absolute -top-1 -right-1 w-4 h-4 bg-[var(--brand-primary)] rounded-full flex items-center justify-center">
                    <svg width="10" height="10" viewBox="0 0 10 10" fill="none">
                      <path 
                        d="M2 5L4 7L8 3" 
                        stroke="white" 
                        strokeWidth="1.5" 
                        strokeLinecap="round" 
                        strokeLinejoin="round"
                      />
                    </svg>
                  </div>
                )}
              </button>
              <button
                type="button"
                onClick={handleCancel}
                className="px-4 py-2 rounded-2xl transition-all text-label border bg-white text-[var(--text-secondary)] border-[var(--border)] flex-shrink-0"
              >
                Отменить
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}