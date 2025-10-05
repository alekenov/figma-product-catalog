export function ProductFooter() {
  return (
    <div className="bg-gray-100 mt-8 px-4 py-6 space-y-6">
      {/* Footer Links */}
      <div className="grid grid-cols-2 gap-8">
        <div className="space-y-2">
          <h4 className="font-semibold text-black">Покупателям</h4>
          <div className="space-y-1 text-sm text-gray-500">
            <p>Магазины</p>
            <p>Для партнёров</p>
            <p>Фото доставки</p>
            <p>Отзывы</p>
          </div>
        </div>
        
        <div className="space-y-2">
          <div className="space-y-1 text-sm text-gray-500">
            <p>Гарантии</p>
            <p>Оплата</p>
            <p>Доставка</p>
            <p>Вакансии</p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-8">
        <div className="space-y-2">
          <h4 className="font-semibold text-black">Компания</h4>
          <div className="space-y-1 text-sm text-gray-500">
            <p>Контакты</p>
            <p>О нас</p>
            <p>Конфиденциальности</p>
          </div>
        </div>
        
        <div className="space-y-2">
          <div className="space-y-1 text-sm text-gray-500">
            <p>Документы</p>
            <p>Новости</p>
            <p>Цветы оптом</p>
          </div>
        </div>
      </div>

      {/* Copyright and Social */}
      <div className="space-y-4">
        <p className="font-bold text-black">© Сvety.kz, 2021</p>
        
        {/* Social Media Icons */}
        <div className="flex gap-4">
          <div className="w-6 h-6 bg-black rounded-full flex items-center justify-center">
            <span className="text-white text-xs">f</span>
          </div>
          <div className="w-6 h-6 bg-black rounded-full flex items-center justify-center">
            <span className="text-white text-xs">YT</span>
          </div>
          <div className="w-6 h-6 bg-black rounded-full flex items-center justify-center">
            <span className="text-white text-xs">IG</span>
          </div>
          <div className="w-6 h-6 bg-black rounded-full flex items-center justify-center">
            <span className="text-white text-xs">VK</span>
          </div>
        </div>

        {/* Payment Methods */}
        <div className="flex gap-2">
          <div className="bg-white rounded px-2 py-1">
            <span className="text-xs text-[#005CA9] font-bold">VISA</span>
          </div>
          <div className="bg-white rounded px-2 py-1 flex">
            <div className="w-2 h-3 bg-[#FE0000] rounded-l"></div>
            <div className="w-2 h-3 bg-[#FE9A00] rounded-r"></div>
          </div>
          <div className="bg-white rounded px-2 py-1">
            <span className="text-xs text-orange-500 font-bold">Kaspi</span>
          </div>
          <div className="bg-white rounded px-2 py-1">
            <span className="text-xs text-[#003087] font-bold">PayPal</span>
          </div>
        </div>
      </div>

      {/* App Download */}
      <div className="space-y-3">
        <h4 className="font-semibold text-black">Приложение</h4>
        <div className="flex gap-2">
          <div className="bg-black rounded px-3 py-2">
            <span className="text-white text-xs">App Store</span>
          </div>
          <div className="bg-black rounded px-3 py-2">
            <span className="text-white text-xs">Google Play</span>
          </div>
        </div>
      </div>
    </div>
  );
}