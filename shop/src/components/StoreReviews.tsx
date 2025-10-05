import { ReviewsList } from './ReviewCard';

export function StoreReviews() {
  const reviews = [
    {
      id: "review-store-1",
      author: "Анна К.",
      date: "22.03.2023",
      rating: 5,
      title: "Отличный магазин!",
      content: "Заказывала букет на день рождения мамы. Качество на высоте, доставили вовремя, мама была в восторге! Обязательно буду заказывать здесь еще.",
      likes: 8,
      dislikes: 0
    },
    {
      id: "review-store-2",
      author: "Максим П.",
      date: "20.03.2023",
      rating: 4,
      title: "Быстрая доставка",
      content: "Нужен был букет срочно, привезли за 30 минут. Цветы свежие, красиво оформлено. Единственное - хотелось бы больше вариантов упаковки.",
      likes: 5,
      dislikes: 1
    },
    {
      id: "review-store-3",
      author: "Елена М.",
      date: "18.03.2023",
      rating: 4,
      title: "Хорошо",
      content: "Неплохой магазин, есть из чего выбрать. Единственное - хотелось бы больше экзотических цветов.",
      likes: 3,
      dislikes: 1
    }
  ];
  
  return (
    <ReviewsList 
      reviews={reviews}
      title="Отзывы (164)"
      compact={true}
      maxItems={3}
    />
  );
}