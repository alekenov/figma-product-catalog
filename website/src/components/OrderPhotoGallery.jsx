import React, { useState } from 'react';

/**
 * OrderPhotoGallery - галерея фотографий заказа с функцией лайк/дизлайк
 *
 * @param {Array} photos - Массив объектов с фото [{url, label, feedback, comment}]
 * @param {string} noticeText - Текст уведомления под галереей
 * @param {Function} onFeedbackSubmit - Callback для отправки фидбека (feedback, comment)
 * @param {boolean} feedbackSubmitted - Флаг, показывающий что фидбек уже отправлен
 */
export default function OrderPhotoGallery({
  photos = [],
  noticeText = 'Мы отправим sms получателю для самостоятельной загрузки фотоотзыва.',
  onFeedbackSubmit = null,
  feedbackSubmitted = false
}) {
  const [selectedFeedback, setSelectedFeedback] = useState(null);
  const [comment, setComment] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Only show if there are photos
  if (!photos || photos.length === 0) {
    return null;
  }

  const photo = photos[0];
  const hasFeedback = feedbackSubmitted || photo.feedback;

  const handleFeedbackClick = (feedbackType) => {
    if (hasFeedback || isSubmitting) return;

    setSelectedFeedback(feedbackType);

    // If like, submit immediately
    if (feedbackType === 'like' && onFeedbackSubmit) {
      handleSubmit(feedbackType, null);
    }
  };

  const handleSubmit = async (feedbackType = selectedFeedback, feedbackComment = comment) => {
    if (!onFeedbackSubmit || isSubmitting) return;

    setIsSubmitting(true);
    try {
      await onFeedbackSubmit(feedbackType, feedbackComment);
    } catch (error) {
      console.error('Failed to submit feedback:', error);
      setIsSubmitting(false);
      setSelectedFeedback(null);
      setComment('');
    }
  };

  return (
    <div className="space-y-4">
      {/* Single Photo - Vertical Layout optimized for mobile */}
      <div className="space-y-2">
        <img
          src={photo.url}
          alt={photo.label || 'Фото заказа'}
          className="w-full h-auto object-contain rounded-lg"
          style={{ maxHeight: '400px' }}
        />
        {photo.label && (
          <p className="font-sans font-normal text-[14px] leading-[1.3] text-text-black">
            {photo.label}
          </p>
        )}
      </div>

      {/* Feedback Section */}
      {onFeedbackSubmit && (
        <div className="space-y-3">
          {/* Show submitted feedback */}
          {hasFeedback && (
            <div className="flex items-start gap-2 p-3 bg-bg-extra-light rounded-lg">
              <span className="text-[24px]">{photo.feedback === 'like' ? '👍' : '👎'}</span>
              <div className="flex-1">
                <p className="font-sans font-semibold text-[14px] text-text-black">
                  {photo.feedback === 'like' ? 'Вам понравился букет' : 'Вы оставили комментарий'}
                </p>
                {photo.comment && (
                  <p className="font-sans font-normal text-[14px] text-text-grey-dark mt-1">
                    {photo.comment}
                  </p>
                )}
              </div>
            </div>
          )}

          {/* Feedback buttons - only show if not submitted */}
          {!hasFeedback && (
            <div className="space-y-3">
              <p className="font-sans font-normal text-[14px] text-text-black">
                Понравился букет?
              </p>

              <div className="flex gap-3">
                <button
                  onClick={() => handleFeedbackClick('like')}
                  disabled={isSubmitting}
                  className="flex items-center justify-center gap-2 px-6 py-3 bg-bg-light hover:bg-bg-extra-light rounded-lg transition-colors disabled:opacity-50"
                >
                  <span className="text-[24px]">👍</span>
                  <span className="font-sans font-medium text-[16px] text-text-black">
                    Да
                  </span>
                </button>

                <button
                  onClick={() => handleFeedbackClick('dislike')}
                  disabled={isSubmitting}
                  className="flex items-center justify-center gap-2 px-6 py-3 bg-bg-light hover:bg-bg-extra-light rounded-lg transition-colors disabled:opacity-50"
                >
                  <span className="text-[24px]">👎</span>
                  <span className="font-sans font-medium text-[16px] text-text-black">
                    Нет
                  </span>
                </button>
              </div>

              {/* Comment field for dislike */}
              {selectedFeedback === 'dislike' && (
                <div className="space-y-2">
                  <label className="font-sans font-normal text-[14px] text-text-black">
                    Что вам не понравилось?
                  </label>
                  <textarea
                    value={comment}
                    onChange={(e) => setComment(e.target.value)}
                    placeholder="Напишите ваш комментарий..."
                    className="w-full p-3 font-sans text-[14px] border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-pink resize-none"
                    rows={4}
                    disabled={isSubmitting}
                  />
                  <button
                    onClick={() => handleSubmit()}
                    disabled={isSubmitting || !comment.trim()}
                    className="w-full py-3 bg-pink text-white font-sans font-semibold text-[16px] rounded-lg hover:bg-pink/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {isSubmitting ? 'Отправка...' : 'Отправить'}
                  </button>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Notice Text */}
      {noticeText && (
        <p className="font-sans font-normal text-[14px] leading-[1.3] text-text-grey-dark">
          {noticeText}
        </p>
      )}
    </div>
  );
}