import { useState } from 'react';
import { CvetyButton } from './ui/cvety-button';
import { ThumbsUp, ThumbsDown, MessageCircle } from 'lucide-react';

interface ReviewProps {
  id: string;
  author: string;
  date: string;
  rating: number;
  title: string;
  content: string;
  likes: number;
  dislikes: number;
  showActions?: boolean;
  compact?: boolean;
}

export function ReviewCard({ 
  id, 
  author, 
  date, 
  rating, 
  title, 
  content, 
  likes, 
  dislikes, 
  showActions = true,
  compact = false 
}: ReviewProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [userLikes, setUserLikes] = useState(likes);
  const [userDislikes, setUserDislikes] = useState(dislikes);
  const [userAction, setUserAction] = useState<'like' | 'dislike' | null>(null);
  
  const shouldTruncate = content.length > 150 && compact;
  const displayContent = shouldTruncate && !isExpanded 
    ? content.slice(0, 150) + '...' 
    : content;
  
  const handleLike = () => {
    if (userAction === 'like') {
      setUserLikes(prev => prev - 1);
      setUserAction(null);
    } else {
      if (userAction === 'dislike') {
        setUserDislikes(prev => prev - 1);
      }
      setUserLikes(prev => prev + 1);
      setUserAction('like');
    }
  };
  
  const handleDislike = () => {
    if (userAction === 'dislike') {
      setUserDislikes(prev => prev - 1);
      setUserAction(null);
    } else {
      if (userAction === 'like') {
        setUserLikes(prev => prev - 1);
      }
      setUserDislikes(prev => prev + 1);
      setUserAction('dislike');
    }
  };
  
  const renderStars = () => {
    return (
      <div className="flex items-center gap-1">
        {[1, 2, 3, 4, 5].map((star) => (
          <svg
            key={star}
            className="w-4 h-4"
            viewBox="0 0 16 16"
            fill={star <= rating ? "var(--brand-warning)" : "var(--neutral-300)"}
          >
            <path d="M8 0l2.4 4.8L16 5.6l-4 3.9L12.8 16 8 13.3 3.2 16 4 9.5 0 5.6l5.6-.8L8 0z" />
          </svg>
        ))}
      </div>
    );
  };
  
  return (
    <div className={`p-[var(--spacing-4)] bg-white rounded-[var(--radius-md)] ${compact ? 'p-[var(--spacing-3)]' : ''}`}>
      <div className="space-y-[var(--spacing-3)]">
        {/* Header */}
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-[var(--spacing-2)] mb-1">
              <span className="text-body-emphasis text-[var(--text-primary)]">{author}</span>
              <span className="text-caption text-[var(--text-secondary)]">{date}</span>
            </div>
            <div className="flex items-center gap-[var(--spacing-2)]">
              {renderStars()}
              {title && (
                <span className="text-caption text-[var(--text-secondary)]">{title}</span>
              )}
            </div>
          </div>
        </div>
        
        {/* Content */}
        <div className="space-y-[var(--spacing-2)]">
          <p className="text-body text-[var(--text-primary)]">
            {displayContent}
          </p>
          
          {shouldTruncate && (
            <button
              onClick={() => setIsExpanded(!isExpanded)}
              className="text-caption text-[var(--brand-primary)] hover:underline"
            >
              {isExpanded ? 'Свернуть' : 'Читать полностью'}
            </button>
          )}
        </div>
        
        {/* Actions */}
        {showActions && (
          <div className="flex items-center gap-[var(--spacing-4)] pt-[var(--spacing-2)] border-t border-[var(--border)]">
            <button
              onClick={handleLike}
              className={`flex items-center gap-1 text-caption transition-colors ${
                userAction === 'like' 
                  ? 'text-[var(--brand-success)]' 
                  : 'text-[var(--text-secondary)] hover:text-[var(--brand-success)]'
              }`}
            >
              <ThumbsUp size={14} />
              <span>{userLikes}</span>
            </button>
            
            <button
              onClick={handleDislike}
              className={`flex items-center gap-1 text-caption transition-colors ${
                userAction === 'dislike' 
                  ? 'text-[var(--brand-error)]' 
                  : 'text-[var(--text-secondary)] hover:text-[var(--brand-error)]'
              }`}
            >
              <ThumbsDown size={14} />
              <span>{userDislikes}</span>
            </button>
            
            <button className="flex items-center gap-1 text-caption text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors">
              <MessageCircle size={14} />
              <span>Ответить</span>
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

interface ReviewsListProps {
  reviews: ReviewProps[];
  title?: string;
  compact?: boolean;
  maxItems?: number;
  showActions?: boolean;
}

export function ReviewsList({ 
  reviews, 
  title = "Отзывы", 
  compact = false, 
  maxItems,
  showActions = true 
}: ReviewsListProps) {
  const [showAll, setShowAll] = useState(false);
  
  const displayedReviews = maxItems && !showAll 
    ? reviews.slice(0, maxItems) 
    : reviews;
  
  const hasMoreReviews = maxItems && reviews.length > maxItems;
  
  return (
    <div className="space-y-[var(--spacing-4)]">
      <div className="flex items-center justify-between">
        <h3 className="text-title text-[var(--text-primary)]">{title}</h3>
        <span className="text-caption text-[var(--text-secondary)]">
          {reviews.length} {reviews.length === 1 ? 'отзыв' : reviews.length < 5 ? 'отзыва' : 'отзывов'}
        </span>
      </div>
      
      <div className="space-y-[var(--spacing-3)]">
        {displayedReviews.map((review) => (
          <ReviewCard 
            key={review.id} 
            {...review} 
            compact={compact}
            showActions={showActions}
          />
        ))}
      </div>
      
      {hasMoreReviews && (
        <div className="text-center">
          <CvetyButton 
            variant="ghost" 
            onClick={() => setShowAll(!showAll)}
          >
            {showAll ? 'Показать меньше' : `Показать все ${reviews.length} отзывов`}
          </CvetyButton>
        </div>
      )}
      
      {reviews.length === 0 && (
        <div className="text-center py-8">
          <p className="text-body text-[var(--text-secondary)]">Отзывов пока нет</p>
          <p className="text-caption text-[var(--text-muted)]">Станьте первым, кто оставит отзыв!</p>
        </div>
      )}
    </div>
  );
}