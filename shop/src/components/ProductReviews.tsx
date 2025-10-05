export function ProductReviews() {
  const reviews = [
    {
      id: 1,
      author: "Alekenov C.",
      date: "15.03.2023",
      rating: 5,
      text: "Один из лучших цветочных магазинов в городе.."
    },
    {
      id: 2,
      author: "Alekenov C.",
      date: "15.03.2023", 
      rating: 5,
      text: "Хороший букет, вовремя доставили"
    },
    {
      id: 3,
      author: "Alekenov C.",
      date: "15.03.2023",
      rating: 5,
      text: "Хороший букет, вовремя доставили"
    }
  ];

  const StarIcon = () => (
    <svg className="w-3 h-3" viewBox="0 0 14 13" fill="none">
      <path d="M7 0L8.5716 4.83688H13.6574L9.5429 7.82624L11.1145 12.6631L7 9.67376L2.8855 12.6631L4.4571 7.82624L0.342604 4.83688H5.4284L7 0Z" fill="#FF6666"/>
    </svg>
  );

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h3 className="text-xl font-medium text-black tracking-wide">Отзывы</h3>
        <p className="text-sm text-black">Смотреть все</p>
      </div>

      {/* Rating Summary */}
      <div className="space-y-2">
        <div className="flex items-center gap-1">
          <StarIcon />
          <span className="text-sm text-black">4.6</span>
        </div>
        <div className="flex items-center gap-2 text-sm text-black">
          <span>164 отзыва</span>
          <span>210 оценок</span>
        </div>
      </div>

      {/* Reviews List */}
      <div className="flex gap-2 overflow-x-auto pb-2">
        {reviews.map((review) => (
          <div key={review.id} className="bg-gray-100 p-4 rounded-lg min-w-[250px] space-y-2">
            <div className="space-y-1">
              <p className="text-black font-medium">{review.author}</p>
              <div className="flex items-center gap-2">
                <div className="flex gap-0.5">
                  {[...Array(5)].map((_, i) => (
                    <StarIcon key={i} />
                  ))}
                </div>
                <span className="text-xs text-gray-500">{review.date}</span>
              </div>
            </div>
            <p className="text-black text-sm leading-tight">{review.text}</p>
          </div>
        ))}
      </div>
    </div>
  );
}