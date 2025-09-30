import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useCart } from '../contexts/CartContext';
import Header from '../components/layout/Header';
import Footer from '../components/layout/Footer';
import ProductHeaderWithRating from '../components/ProductHeaderWithRating';
import ProductImageGallery from '../components/ProductImageGallery';
import SizeSelector from '../components/SizeSelector';
import CompositionSection from '../components/CompositionSection';
import AdditionalOptions from '../components/AdditionalOptions';
import FrequentlyBoughtTogether from '../components/FrequentlyBoughtTogether';
import PickupSection from '../components/PickupSection';
import ExpandableSection from '../components/ExpandableSection';
import ReviewsTabs from '../components/ReviewsTabs';
import DetailedReviewsSection from '../components/DetailedReviewsSection';
import CvetyButton from '../components/ui/CvetyButton';

// Mock данные товара (обновленная версия по новому дизайну)
const mockProduct = {
  id: 1,
  name: 'Букет розовых пионов',
  size: '1-20 см',
  rating: 4.8,
  reviewCount: 58,
  ratingCount: 210,
  mainPrice: '22 500 ₸',
  images: [
    'https://s3-alpha-sig.figma.com/img/a763/c5f3/3269c2bbd4306454e16d47682fec708c?Expires=1760313600&Key-Pair-Id=APKAQ4GOSFWCW27IBOMQ&Signature=mrvVrVwyH8DUFwzceEHA1PjjKPGiqRpLG8PcMIQjA0RSBazjJaVoADQCoHTrTY3M~w1lloEgtIVB1-WjG1j3jU00cwXm0fbOGoOIWT3bX63XeDRsEC9n8-r7RBma2kCyoetfzoexpVP1-htX8Bfpb26vPpqDwgbyDgDi1uh8vU2T2YK5TG0ZWL5gqK1ClFGdhjRfyzu85Bnsw8mGIxUBSXzaEqWj6HgXr2ILliifVibSmIetu8O0jPlecloyzihk9o2y8PCTIE3GFPXDI0Cd9AHC5id3yVsUBWBL31haynW5jMETg~h~Z8jV4cs42uB1XXOZQ7-dnCo3nmqv7D~h3A__',
    'https://s3-alpha-sig.figma.com/img/4383/50a0/f5172f1ab210cb733df6869e0b9f8ef5?Expires=1760313600&Key-Pair-Id=APKAQ4GOSFWCW27IBOMQ&Signature=lYC3Fr7o-thSASyeM83OzIwund7RFXV-k5X5qA1keits0702vrJ4EfErOmZQ1z7Mbf6oX6VuQa4nAlcXrWn81FqAqbXpohBnEmEhuFopGVI1y0dzUNTtPwE62pRuJil6ULoafDUXtySbkVROlqfuPlXaETav7vrywawSrzf92V7dKIWB-5WNdoHe-KPu~kUu3eiQmL6YcR7FGWgtbUBivnZnYuR~KaY1HLyeKkidbbveYQBI4865fL8~MjybzAwpdLmuMi0RQX-m5c74Wa3bR170y0yP8VAWSURPoAd2BCLwehRlCr6pg9YzIaaX1zxrxLT38MDjSBGDIaTSjmJCHg__'
  ],
  sizes: [
    { id: 's', label: 'S', price: '15 000 ₸' },
    { id: 'm', label: 'M', price: '22 500 ₸' },
    { id: 'l', label: 'L', price: '30 000 ₸' },
    { id: 'xl', label: 'XL', price: '40 000 ₸' }
  ],
  composition: [
    { id: 1, name: 'Роза розовая', quantity: 15 },
    { id: 2, name: 'Пион розовый', quantity: 7 },
    { id: 3, name: 'Эвкалипт', quantity: 3 },
    { id: 4, name: 'Зелень декоративная', quantity: 5 }
  ],
  additionalOptions: [
    { id: 1, label: 'Добавить упаковочную ленту и бумагу', checked: false },
    { id: 2, label: 'Добавить открытку (бесплатно)', checked: false }
  ],
  frequentlyBought: [
    {
      id: 101,
      name: 'Коробка конфет Raffaello',
      price: '3 500 ₸',
      image: 'https://s3-alpha-sig.figma.com/img/a763/c5f3/3269c2bbd4306454e16d47682fec708c?Expires=1760313600&Key-Pair-Id=APKAQ4GOSFWCW27IBOMQ&Signature=mrvVrVwyH8DUFwzceEHA1PjjKPGiqRpLG8PcMIQjA0RSBazjJaVoADQCoHTrTY3M~w1lloEgtIVB1-WjG1j3jU00cwXm0fbOGoOIWT3bX63XeDRsEC9n8-r7RBma2kCyoetfzoexpVP1-htX8Bfpb26vPpqDwgbyDgDi1uh8vU2T2YK5TG0ZWL5gqK1ClFGdhjRfyzu85Bnsw8mGIxUBSXzaEqWj6HgXr2ILliifVibSmIetu8O0jPlecloyzihk9o2y8PCTIE3GFPXDI0Cd9AHC5id3yVsUBWBL31haynW5jMETg~h~Z8jV4cs42uB1XXOZQ7-dnCo3nmqv7D~h3A__'
    },
    {
      id: 102,
      name: 'Мягкая игрушка Мишка',
      price: '4 500 ₸',
      image: 'https://s3-alpha-sig.figma.com/img/4383/50a0/f5172f1ab210cb733df6869e0b9f8ef5?Expires=1760313600&Key-Pair-Id=APKAQ4GOSFWCW27IBOMQ&Signature=lYC3Fr7o-thSASyeM83OzIwund7RFXV-k5X5qA1keits0702vrJ4EfErOmZQ1z7Mbf6oX6VuQa4nAlcXrWn81FqAqbXpohBnEmEhuFopGVI1y0dzUNTtPwE62pRuJil6ULoafDUXtySbkVROlqfuPlXaETav7vrywawSrzf92V7dKIWB-5WNdoHe-KPu~kUu3eiQmL6YcR7FGWgtbUBivnZnYuR~KaY1HLyeKkidbbveYQBI4865fL8~MjybzAwpdLmuMi0RQX-m5c74Wa3bR170y0yP8VAWSURPoAd2BCLwehRlCr6pg9YzIaaX1zxrxLT38MDjSBGDIaTSjmJCHg__'
    },
    {
      id: 103,
      name: 'Шампанское Moët & Chandon',
      price: '12 000 ₸',
      image: 'https://s3-alpha-sig.figma.com/img/a763/c5f3/3269c2bbd4306454e16d47682fec708c?Expires=1760313600&Key-Pair-Id=APKAQ4GOSFWCW27IBOMQ&Signature=mrvVrVwyH8DUFwzceEHA1PjjKPGiqRpLG8PcMIQjA0RSBazjJaVoADQCoHTrTY3M~w1lloEgtIVB1-WjG1j3jU00cwXm0fbOGoOIWT3bX63XeDRsEC9n8-r7RBma2kCyoetfzoexpVP1-htX8Bfpb26vPpqDwgbyDgDi1uh8vU2T2YK5TG0ZWL5gqK1ClFGdhjRfyzu85Bnsw8mGIxUBSXzaEqWj6HgXr2ILliifVibSmIetu8O0jPlecloyzihk9o2y8PCTIE3GFPXDI0Cd9AHC5id3yVsUBWBL31haynW5jMETg~h~Z8jV4cs42uB1XXOZQ7-dnCo3nmqv7D~h3A__'
    }
  ],
  pickupAddresses: [
    'ул. Достык, 123 (ТЦ Dostyk Plaza)',
    'пр. Абая, 45 (рядом с метро Абай)',
    'ул. Байзакова, 67 (ТРЦ Mega Silk Way)'
  ],
  description: 'Нежный букет из розовых пионов и роз. Идеальный подарок для особенного человека. Каждый цветок тщательно отобран флористами с учетом свежести и красоты. Букет дополнен декоративной зеленью и эвкалиптом, что придает композиции объем и изысканность.',
  productReviews: {
    count: 58,
    averageRating: 4.8,
    ratingBreakdown: {
      5: 45,
      4: 10,
      3: 2,
      2: 0,
      1: 1
    },
    photos: [
      { id: 1, url: 'https://s3-alpha-sig.figma.com/img/a763/c5f3/3269c2bbd4306454e16d47682fec708c?Expires=1760313600&Key-Pair-Id=APKAQ4GOSFWCW27IBOMQ&Signature=mrvVrVwyH8DUFwzceEHA1PjjKPGiqRpLG8PcMIQjA0RSBazjJaVoADQCoHTrTY3M~w1lloEgtIVB1-WjG1j3jU00cwXm0fbOGoOIWT3bX63XeDRsEC9n8-r7RBma2kCyoetfzoexpVP1-htX8Bfpb26vPpqDwgbyDgDi1uh8vU2T2YK5TG0ZWL5gqK1ClFGdhjRfyzu85Bnsw8mGIxUBSXzaEqWj6HgXr2ILliifVibSmIetu8O0jPlecloyzihk9o2y8PCTIE3GFPXDI0Cd9AHC5id3yVsUBWBL31haynW5jMETg~h~Z8jV4cs42uB1XXOZQ7-dnCo3nmqv7D~h3A__' },
      { id: 2, url: 'https://s3-alpha-sig.figma.com/img/4383/50a0/f5172f1ab210cb733df6869e0b9f8ef5?Expires=1760313600&Key-Pair-Id=APKAQ4GOSFWCW27IBOMQ&Signature=lYC3Fr7o-thSASyeM83OzIwund7RFXV-k5X5qA1keits0702vrJ4EfErOmZQ1z7Mbf6oX6VuQa4nAlcXrWn81FqAqbXpohBnEmEhuFopGVI1y0dzUNTtPwE62pRuJil6ULoafDUXtySbkVROlqfuPlXaETav7vrywawSrzf92V7dKIWB-5WNdoHe-KPu~kUu3eiQmL6YcR7FGWgtbUBivnZnYuR~KaY1HLyeKkidbbveYQBI4865fL8~MjybzAwpdLmuMi0RQX-m5c74Wa3bR170y0yP8VAWSURPoAd2BCLwehRlCr6pg9YzIaaX1zxrxLT38MDjSBGDIaTSjmJCHg__' },
      { id: 3, url: 'https://s3-alpha-sig.figma.com/img/a763/c5f3/3269c2bbd4306454e16d47682fec708c?Expires=1760313600&Key-Pair-Id=APKAQ4GOSFWCW27IBOMQ&Signature=mrvVrVwyH8DUFwzceEHA1PjjKPGiqRpLG8PcMIQjA0RSBazjJaVoADQCoHTrTY3M~w1lloEgtIVB1-WjG1j3jU00cwXm0fbOGoOIWT3bX63XeDRsEC9n8-r7RBma2kCyoetfzoexpVP1-htX8Bfpb26vPpqDwgbyDgDi1uh8vU2T2YK5TG0ZWL5gqK1ClFGdhjRfyzu85Bnsw8mGIxUBSXzaEqWj6HgXr2ILliifVibSmIetu8O0jPlecloyzihk9o2y8PCTIE3GFPXDI0Cd9AHC5id3yVsUBWBL31haynW5jMETg~h~Z8jV4cs42uB1XXOZQ7-dnCo3nmqv7D~h3A__' }
    ],
    items: [
      {
        id: 1,
        author: 'Айгерим Смагулова',
        avatar: null,
        date: '15 февраля 2025',
        rating: 5,
        text: 'Заказывала этот букет на день рождения мамы. Цветы пришли свежие, красивые, ровно как на фотографии! Мама была в восторге. Спасибо большое за качество и сервис!',
        photos: ['https://s3-alpha-sig.figma.com/img/a763/c5f3/3269c2bbd4306454e16d47682fec708c?Expires=1760313600&Key-Pair-Id=APKAQ4GOSFWCW27IBOMQ&Signature=mrvVrVwyH8DUFwzceEHA1PjjKPGiqRpLG8PcMIQjA0RSBazjJaVoADQCoHTrTY3M~w1lloEgtIVB1-WjG1j3jU00cwXm0fbOGoOIWT3bX63XeDRsEC9n8-r7RBma2kCyoetfzoexpVP1-htX8Bfpb26vPpqDwgbyDgDi1uh8vU2T2YK5TG0ZWL5gqK1ClFGdhjRfyzu85Bnsw8mGIxUBSXzaEqWj6HgXr2ILliifVibSmIetu8O0jPlecloyzihk9o2y8PCTIE3GFPXDI0Cd9AHC5id3yVsUBWBL31haynW5jMETg~h~Z8jV4cs42uB1XXOZQ7-dnCo3nmqv7D~h3A__'],
        likes: 24,
        dislikes: 1
      },
      {
        id: 2,
        author: 'Дмитрий Петров',
        avatar: null,
        date: '10 февраля 2025',
        rating: 5,
        text: 'Отличный букет! Доставили вовремя, цветы свежие и ароматные. Жена очень довольна. Обязательно буду заказывать ещё.',
        photos: [],
        likes: 18,
        dislikes: 0
      },
      {
        id: 3,
        author: 'Светлана Ким',
        avatar: null,
        date: '5 февраля 2025',
        rating: 4,
        text: 'Букет красивый, но немного меньше, чем ожидала по размеру M. В остальном всё отлично - цветы свежие, доставка быстрая.',
        photos: ['https://s3-alpha-sig.figma.com/img/4383/50a0/f5172f1ab210cb733df6869e0b9f8ef5?Expires=1760313600&Key-Pair-Id=APKAQ4GOSFWCW27IBOMQ&Signature=lYC3Fr7o-thSASyeM83OzIwund7RFXV-k5X5qA1keits0702vrJ4EfErOmZQ1z7Mbf6oX6VuQa4nAlcXrWn81FqAqbXpohBnEmEhuFopGVI1y0dzUNTtPwE62pRuJil6ULoafDUXtySbkVROlqfuPlXaETav7vrywawSrzf92V7dKIWB-5WNdoHe-KPu~kUu3eiQmL6YcR7FGWgtbUBivnZnYuR~KaY1HLyeKkidbbveYQBI4865fL8~MjybzAwpdLmuMi0RQX-m5c74Wa3bR170y0yP8VAWSURPoAd2BCLwehRlCr6pg9YzIaaX1zxrxLT38MDjSBGDIaTSjmJCHg__'],
        likes: 12,
        dislikes: 2
      }
    ]
  },
  companyReviews: {
    count: 342,
    averageRating: 4.7,
    ratingBreakdown: {
      5: 250,
      4: 70,
      3: 15,
      2: 5,
      1: 2
    },
    photos: [],
    items: [
      {
        id: 11,
        author: 'Алия Нурбекова',
        avatar: null,
        date: '20 февраля 2025',
        rating: 5,
        text: 'Заказываю цветы в этой компании уже третий раз. Всегда свежие цветы, вежливые курьеры, быстрая доставка. Очень рекомендую!',
        photos: [],
        likes: 45,
        dislikes: 1
      },
      {
        id: 12,
        author: 'Марат Тулеев',
        avatar: null,
        date: '18 февраля 2025',
        rating: 5,
        text: 'Лучший сервис доставки цветов в Астане! Всегда выручают, даже когда заказываешь в последний момент.',
        photos: [],
        likes: 38,
        dislikes: 0
      }
    ]
  }
};

export default function ProductDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { addToCart, getCartCount } = useCart();

  // State management
  const [selectedSize, setSelectedSize] = useState('m');
  const [additionalOptions, setAdditionalOptions] = useState(mockProduct.additionalOptions);
  const [pickupChecked, setPickupChecked] = useState(false);
  const [activeReviewTab, setActiveReviewTab] = useState('product');

  // Handlers
  const handleSizeSelect = (sizeId) => {
    setSelectedSize(sizeId);
  };

  const handleOptionToggle = (optionId, checked) => {
    setAdditionalOptions(prev =>
      prev.map(opt => opt.id === optionId ? { ...opt, checked } : opt)
    );
  };

  const handleFrequentlyBoughtToggle = (selectedProducts) => {
    console.log('Selected products:', selectedProducts);
  };

  const handleAddToCart = () => {
    const selectedSizeData = mockProduct.sizes.find(s => s.id === selectedSize);

    // Parse price value from string (e.g., "22 500 ₸" -> 22500)
    const priceValue = parseInt(selectedSizeData.price.replace(/\s/g, '').replace('₸', ''));

    const cartItem = {
      productId: mockProduct.id,
      name: mockProduct.name,
      image: mockProduct.images[0],
      size: selectedSizeData.label,
      price: selectedSizeData.price,
      priceValue: priceValue,
      quantity: 1,
      options: additionalOptions.filter(opt => opt.checked)
    };

    addToCart(cartItem);
    navigate('/cart');
  };

  const handleLoadMoreReviews = () => {
    console.log('Load more reviews');
  };

  // Get current price based on selected size
  const currentPrice = mockProduct.sizes.find(s => s.id === selectedSize)?.price || mockProduct.mainPrice;

  // Get current reviews based on active tab
  const currentReviews = activeReviewTab === 'product'
    ? mockProduct.productReviews
    : mockProduct.companyReviews;

  return (
    <div className="bg-white min-h-screen w-full max-w-sm mx-auto flex flex-col">
      <Header cartCount={getCartCount()} />

      <main className="flex-1 px-4 py-6 space-y-6">
          {/* Product Header with Rating */}
          <ProductHeaderWithRating
            name={mockProduct.name}
            rating={mockProduct.rating}
            reviewCount={mockProduct.reviewCount}
            ratingCount={mockProduct.ratingCount}
            size={mockProduct.size}
          />

          {/* Product Image Gallery */}
          <ProductImageGallery
            images={mockProduct.images}
            alt={mockProduct.name}
          />

          {/* Price */}
          <div className="font-sans font-bold text-h1 text-text-black">
            {currentPrice}
          </div>

          {/* Size Selector */}
          <SizeSelector
            sizes={mockProduct.sizes}
            selectedSize={selectedSize}
            onSizeSelect={handleSizeSelect}
          />

          {/* Composition */}
          <CompositionSection items={mockProduct.composition} />

          {/* Additional Options */}
          <AdditionalOptions
            title="Дополнительно"
            options={additionalOptions}
            onOptionToggle={handleOptionToggle}
          />

          {/* Frequently Bought Together */}
          <FrequentlyBoughtTogether
            products={mockProduct.frequentlyBought}
            onProductToggle={handleFrequentlyBoughtToggle}
          />

          {/* Primary Purchase Button */}
          <CvetyButton
            variant="primary"
            size="lg"
            fullWidth
            onClick={handleAddToCart}
            className="font-bold"
          >
            {currentPrice} в корзину
          </CvetyButton>

          {/* Pickup Section */}
          <PickupSection
            checked={pickupChecked}
            onChange={setPickupChecked}
            addresses={mockProduct.pickupAddresses}
          />

          {/* Description (Expandable) */}
          <ExpandableSection title="Описание" defaultExpanded={false}>
            <p className="font-sans font-normal text-body-2 text-text-black">
              {mockProduct.description}
            </p>
          </ExpandableSection>

          {/* Delivery Info (Expandable) */}
          <ExpandableSection title="Доставка и оплата" defaultExpanded={false}>
            <div className="space-y-2 font-sans font-normal text-body-2 text-text-black">
              <p>Доставка по Астане - 1500 ₸</p>
              <p>Бесплатная доставка при заказе от 15 000 ₸</p>
              <p>Оплата: наличные, Kaspi, картой</p>
              <p>Доставка в течение 2-4 часов</p>
            </div>
          </ExpandableSection>

          {/* Reviews Section */}
          <div className="space-y-4">
            <h2 className="font-sans font-bold text-h2 text-text-black">
              Отзывы
            </h2>

            {/* Reviews Tabs */}
            <ReviewsTabs
              productReviewsCount={mockProduct.productReviews.count}
              companyReviewsCount={mockProduct.companyReviews.count}
              onTabChange={setActiveReviewTab}
            />

            {/* Detailed Reviews */}
            <DetailedReviewsSection
              averageRating={currentReviews.averageRating}
              totalReviews={currentReviews.count}
              ratingBreakdown={currentReviews.ratingBreakdown}
              reviewPhotos={currentReviews.photos}
              reviews={currentReviews.items}
              onLoadMore={handleLoadMoreReviews}
              hasMore={currentReviews.items.length < currentReviews.count}
            />
          </div>
        </main>

      <Footer />
    </div>
  );
}