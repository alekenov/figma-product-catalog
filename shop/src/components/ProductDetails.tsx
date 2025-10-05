import imgImage395 from "figma:asset/0b8909435cb73a7468d59ef5284779e6da134cfd.png";
import imgImage396 from "figma:asset/079133d9e2bf4b4dbee34cb1f72bb22184975dbc.png";
import { CvetyTextarea } from './ui/cvety-textarea';
import { useState } from 'react';

export function ProductDetails() {
  const [comment, setComment] = useState('');
  const [selectedCertificate, setSelectedCertificate] = useState<string | null>(null);

  const certificates = [
    {
      id: 'spa',
      image: imgImage395,
      title: 'Электронный сертификат в SPA от 1 часа',
      description: 'Вид массажа сможете выбрать в салоне'
    },
    {
      id: 'lingerie',
      image: imgImage396,
      title: 'Электронный сертификат на покупку нижнего белья',
      description: 'Выбрать бельё сможете в магазине Ab bra'
    }
  ];

  return (
    <div className="space-y-[var(--spacing-6)]">
      {/* Delivery Info */}
      <div className="p-[var(--spacing-4)] bg-white rounded-[var(--radius-md)] space-y-[var(--spacing-3)]">
        <div className="space-y-[var(--spacing-2)]">
          <p className="text-[var(--text-primary)]">Город доставки - Астана</p>
          <p className="text-[var(--text-primary)]">Доставка - 1500 ₸</p>
          <p className="text-[var(--text-primary)]">Ближайшая сегодня к 11:20</p>
        </div>
        <div className="space-y-[var(--spacing-2)]">
          <p className="text-[var(--text-primary)]">Или самовывоз по адресу:</p>
          <p className="text-[var(--text-primary)] font-medium underline">Достык 5 к 11:30</p>
        </div>
      </div>

      {/* Comment Field */}
      <div className="p-[var(--spacing-4)] bg-white rounded-[var(--radius-md)] space-y-[var(--spacing-3)]">
        <p className="text-[var(--text-primary)] font-medium">Добавьте данные для персонализации</p>
        <CvetyTextarea
          value={comment}
          onChange={(e) => setComment(e.target.value)}
          placeholder="Ваш комментарий"
          className="min-h-[60px]"
        />
      </div>

      {/* E-certificates */}
      <div className="p-[var(--spacing-4)] bg-white rounded-[var(--radius-md)] space-y-[var(--spacing-4)]">
        <p className="text-[var(--text-primary)] font-medium">Добавьте к заказу электронный сертификат</p>
        
        <div className="space-y-[var(--spacing-3)]">
          {certificates.map((certificate) => (
            <button
              key={certificate.id}
              onClick={() => setSelectedCertificate(
                selectedCertificate === certificate.id ? null : certificate.id
              )}
              className="relative w-full flex bg-white border border-[var(--border)] rounded-[var(--radius-md)] overflow-hidden transition-all"
            >
              <img 
                src={certificate.image} 
                alt={certificate.title}
                className="w-20 h-20 object-cover flex-shrink-0"
              />
              <div className="flex-1 p-[var(--spacing-3)] text-left space-y-[var(--spacing-1)]">
                <div className="text-[var(--text-primary)] space-y-1">
                  <p className="font-medium">{certificate.title.split(' ').slice(0, 3).join(' ')}</p>
                  <p className="font-medium">{certificate.title.split(' ').slice(3).join(' ')}</p>
                </div>
                <p className="text-[var(--text-secondary)] text-sm">
                  {certificate.description}
                </p>
              </div>
              
              {selectedCertificate === certificate.id && (
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
          ))}
        </div>
      </div>

      {/* Questions */}
      <div className="p-[var(--spacing-4)] bg-white rounded-[var(--radius-md)]">
        <p className="text-[var(--text-primary)]">
          Остались вопросы? <span className="text-[var(--brand-primary)] font-medium">Ответим в чате</span>
        </p>
      </div>

      {/* Payment Methods */}
      <div className="p-[var(--spacing-4)] bg-white rounded-[var(--radius-md)]">
        <div className="flex gap-[var(--spacing-2)]">
          {/* Visa */}
          <div className="bg-white border border-[var(--border)] rounded-[var(--radius-sm)] px-2 py-1">
            <div className="w-12 h-5 bg-[#005CA9] rounded-sm flex items-center justify-center">
              <span className="text-white text-xs font-bold">VISA</span>
            </div>
          </div>
          
          {/* Mastercard */}
          <div className="bg-white border border-[var(--border)] rounded-[var(--radius-sm)] px-2 py-1">
            <div className="w-6 h-5 flex">
              <div className="w-3 h-5 bg-[#FE0000] rounded-l-full"></div>
              <div className="w-3 h-5 bg-[#FE9A00] rounded-r-full"></div>
            </div>
          </div>
          
          {/* Kaspi */}
          <div className="bg-white border border-[var(--border)] rounded-[var(--radius-sm)] px-2 py-1">
            <div className="w-12 h-5 bg-gradient-to-r from-red-500 to-orange-500 rounded-sm"></div>
          </div>
          
          {/* PayPal */}
          <div className="bg-white border border-[var(--border)] rounded-[var(--radius-sm)] px-2 py-1">
            <div className="w-12 h-5 bg-[#003087] rounded-sm flex items-center justify-center">
              <span className="text-white text-xs">PayPal</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}