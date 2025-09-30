import React, { useState, useEffect } from 'react';
import FAQItem from './FAQItem';
import { fetchFAQs } from '../services/api';

/**
 * FAQSection - секция часто задаваемых вопросов
 */
export default function FAQSection() {
  const [faqs, setFaqs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function loadFAQs() {
      try {
        setLoading(true);
        const data = await fetchFAQs(); // Fetch all FAQs
        setFaqs(data || []);
        setError(null);
      } catch (err) {
        console.error('Failed to load FAQs:', err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }

    loadFAQs();
  }, []);
  if (loading) {
    return (
      <div className="content-stretch flex flex-col items-start relative w-full">
        <h2 className="font-sans font-bold text-h2 text-text-black mb-7">
          Часто задаваемые вопросы
        </h2>
        <div className="font-sans font-normal text-body2 text-text-grey-dark">
          Загрузка вопросов...
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="content-stretch flex flex-col items-start relative w-full">
        <h2 className="font-sans font-bold text-h2 text-text-black mb-7">
          Часто задаваемые вопросы
        </h2>
        <div className="font-sans font-normal text-body2 text-text-grey-dark">
          Не удалось загрузить вопросы
        </div>
      </div>
    );
  }

  return (
    <div className="content-stretch flex flex-col items-start relative w-full">
      {/* Заголовок */}
      <h2 className="font-sans font-bold text-h2 text-text-black mb-7">
        Часто задаваемые вопросы
      </h2>

      {/* Список вопросов */}
      <div className="content-stretch flex flex-col gap-2 items-start relative shrink-0 w-full">
        {faqs.length > 0 ? (
          faqs.map((faq, index) => (
            <FAQItem
              key={faq.id}
              question={faq.question}
              answer={faq.answer}
              defaultOpen={index === 1} // Второй вопрос открыт по умолчанию (как в дизайне)
            />
          ))
        ) : (
          <div className="font-sans font-normal text-body2 text-text-grey-dark">
            Пока нет вопросов
          </div>
        )}
      </div>
    </div>
  );
}