import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useCart } from '../contexts/CartContext';
import Header from '../components/layout/Header';
import CategoryNav from '../components/layout/CategoryNav';
import Footer from '../components/layout/Footer';
import ProductCard from '../components/ProductCard';
import SectionHeader from '../components/SectionHeader';
import FilterTags, { FilterIcons } from '../components/FilterTags';
import ReviewsSection from '../components/ReviewsSection';
import FAQSection from '../components/FAQSection';
import CvetyButton from '../components/ui/CvetyButton';

// Mock data для товаров
const mockProducts = [
  {
    id: 1,
    image: 'https://s3-alpha-sig.figma.com/img/a763/c5f3/3269c2bbd4306454e16d47682fec708c?Expires=1760313600&Key-Pair-Id=APKAQ4GOSFWCW27IBOMQ&Signature=mrvVrVwyH8DUFwzceEHA1PjjKPGiqRpLG8PcMIQjA0RSBazjJaVoADQCoHTrTY3M~w1lloEgtIVB1-WjG1j3jU00cwXm0fbOGoOIWT3bX63XeDRsEC9n8-r7RBma2kCyoetfzoexpVP1-htX8Bfpb26vPpqDwgbyDgDi1uh8vU2T2YK5TG0ZWL5gqK1ClFGdhjRfyzu85Bnsw8mGIxUBSXzaEqWj6HgXr2ILliifVibSmIetu8O0jPlecloyzihk9o2y8PCTIE3GFPXDI0Cd9AHC5id3yVsUBWBL31haynW5jMETg~h~Z8jV4cs42uB1XXOZQ7-dnCo3nmqv7D~h3A__',
    price: '7 900 ₸',
    name: 'Розовые розы с оформлением',
    deliveryText: 'Доставим завтра к 15:30'
  },
  {
    id: 2,
    image: 'https://s3-alpha-sig.figma.com/img/4383/50a0/f5172f1ab210cb733df6869e0b9f8ef5?Expires=1760313600&Key-Pair-Id=APKAQ4GOSFWCW27IBOMQ&Signature=lYC3Fr7o-thSASyeM83OzIwund7RFXV-k5X5qA1keits0702vrJ4EfErOmZQ1z7Mbf6oX6VuQa4nAlcXrWn81FqAqbXpohBnEmEhuFopGVI1y0dzUNTtPwE62pRuJil6ULoafDUXtySbkVROlqfuPlXaETav7vrywawSrzf92V7dKIWB-5WNdoHe-KPu~kUu3eiQmL6YcR7FGWgtbUBivnZnYuR~KaY1HLyeKkidbbveYQBI4865fL8~MjybzAwpdLmuMi0RQX-m5c74Wa3bR170y0yP8VAWSURPoAd2BCLwehRlCr6pg9YzIaaX1zxrxLT38MDjSBGDIaTSjmJCHg__',
    price: '12 500 ₸',
    name: 'Букет из пионов',
    deliveryText: 'Доставим сегодня к 15:30'
  },
  {
    id: 3,
    image: 'https://s3-alpha-sig.figma.com/img/a763/c5f3/3269c2bbd4306454e16d47682fec708c?Expires=1760313600&Key-Pair-Id=APKAQ4GOSFWCW27IBOMQ&Signature=mrvVrVwyH8DUFwzceEHA1PjjKPGiqRpLG8PcMIQjA0RSBazjJaVoADQCoHTrTY3M~w1lloEgtIVB1-WjG1j3jU00cwXm0fbOGoOIWT3bX63XeDRsEC9n8-r7RBma2kCyoetfzoexpVP1-htX8Bfpb26vPpqDwgbyDgDi1uh8vU2T2YK5TG0ZWL5gqK1ClFGdhjRfyzu85Bnsw8mGIxUBSXzaEqWj6HgXr2ILliifVibSmIetu8O0jPlecloyzihk9o2y8PCTIE3GFPXDI0Cd9AHC5id3yVsUBWBL31haynW5jMETg~h~Z8jV4cs42uB1XXOZQ7-dnCo3nmqv7D~h3A__',
    price: '8 900 ₸',
    name: 'Нежный букет роз',
    deliveryText: 'Доставим завтра'
  },
  {
    id: 4,
    image: 'https://s3-alpha-sig.figma.com/img/4383/50a0/f5172f1ab210cb733df6869e0b9f8ef5?Expires=1760313600&Key-Pair-Id=APKAQ4GOSFWCW27IBOMQ&Signature=lYC3Fr7o-thSASyeM83OzIwund7RFXV-k5X5qA1keits0702vrJ4EfErOmZQ1z7Mbf6oX6VuQa4nAlcXrWn81FqAqbXpohBnEmEhuFopGVI1y0dzUNTtPwE62pRuJil6ULoafDUXtySbkVROlqfuPlXaETav7vrywawSrzf92V7dKIWB-5WNdoHe-KPu~kUu3eiQmL6YcR7FGWgtbUBivnZnYuR~KaY1HLyeKkidbbveYQBI4865fL8~MjybzAwpdLmuMi0RQX-m5c74Wa3bR170y0yP8VAWSURPoAd2BCLwehRlCr6pg9YzIaaX1zxrxLT38MDjSBGDIaTSjmJCHg__',
    price: '15 000 ₸',
    name: 'Премиум букет',
    deliveryText: 'Доставим сегодня к 18:00'
  }
];

// Теги фильтров
const filterTags = [
  { id: 'urgent', label: 'Срочно', icon: <FilterIcons.Lightning /> },
  { id: 'budget', label: 'Бюджетные', icon: <FilterIcons.Star /> },
  { id: 'discount', label: 'Скидки' },
  { id: 'mono', label: 'Монобукеты' },
  { id: 'roses', label: 'Розы' },
  { id: 'mom', label: 'Маме' },
  { id: 'valentine', label: '14 февраля' },
  { id: 'wholesale', label: 'Оптом' },
  { id: 'pickup', label: 'Самовывоз' }
];

export default function HomePage() {
  const navigate = useNavigate();
  const { getCartCount } = useCart();
  const [activeTags, setActiveTags] = useState([]);

  const handleTagClick = (tagId) => {
    setActiveTags(prev =>
      prev.includes(tagId)
        ? prev.filter(id => id !== tagId)
        : [...prev, tagId]
    );
  };

  const handleAddToCart = (productId) => {
    console.log('Add to cart:', productId);
  };

  const handleProductClick = (productId) => {
    navigate(`/product/${productId}`);
  };

  return (
    <div className="bg-white min-h-screen w-full max-w-sm mx-auto flex flex-col">
      {/* Header */}
      <Header cartCount={getCartCount()} />

      {/* Category Navigation */}
      <CategoryNav />

      {/* Main Content */}
      <main className="flex-1 px-4 py-6 space-y-6">
          {/* Page Title + Filter Button */}
          <div className="flex items-center justify-between">
            <h1 className="font-sans font-bold leading-normal text-h2 text-text-black">
              Доставка цветов в Астане
            </h1>
            <CvetyButton
              variant="ghost"
              size="sm"
              aria-label="Фильтры"
              rightIcon={
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                  <path
                    d="M4 6h16M7 12h10M10 18h4"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                  />
                </svg>
              }
            >
              Фильтры
            </CvetyButton>
          </div>

          {/* Filter Tags */}
          <FilterTags
            tags={filterTags}
            activeTags={activeTags}
            onTagClick={handleTagClick}
          />

          {/* Bestsellers Section */}
          <div className="space-y-4">
            <SectionHeader
              title="Букеты-бестселлеры"
              onShowAll={() => console.log('Show all bestsellers')}
            />

            {/* Product Grid - 2 columns */}
            <div className="grid grid-cols-2 gap-4">
              {mockProducts.map(product => (
                <ProductCard
                  key={product.id}
                  image={product.image}
                  price={product.price}
                  name={product.name}
                  deliveryText={product.deliveryText}
                  onAddToCart={() => handleAddToCart(product.id)}
                  onClick={() => handleProductClick(product.id)}
                />
              ))}
            </div>
          </div>

          {/* Reviews Section */}
          <ReviewsSection onShowAll={() => console.log('Show all reviews')} />

          {/* FAQ Section */}
          <FAQSection />
        </main>

      {/* Footer */}
      <Footer />
    </div>
  );
}