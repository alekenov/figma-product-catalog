import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useCart } from '../contexts/CartContext';
import { fetchProductDetail } from '../services/api';
import { formatPrice, kopecksToTenge } from '../utils/price';
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

export default function ProductDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { addToCart, getCartCount } = useCart();

  // API state
  const [product, setProduct] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // UI state management
  const [selectedSize, setSelectedSize] = useState(null);
  const [additionalOptions, setAdditionalOptions] = useState([]);
  const [pickupChecked, setPickupChecked] = useState(false);
  const [activeReviewTab, setActiveReviewTab] = useState('product');

  // Fetch product data
  useEffect(() => {
    async function loadProduct() {
      try {
        setLoading(true);
        const data = await fetchProductDetail(id);

        // Transform API response to frontend format
        const normalizedComposition = Array.isArray(data.composition)
          ? data.composition
          : [];

        const normalizedVariants = Array.isArray(data.variants)
          ? data.variants
          : [];

        const descriptionText = data.description || '';

        const transformedProduct = {
          id: data.id,
          name: data.name,
          rating: data.rating || 0,
          reviewCount: data.review_count || 0,
          ratingCount: data.rating_count || 0,
          mainPrice: formatPrice(data.price),
          mainPriceValue: kopecksToTenge(data.price),
          sizeDescription: data.width && data.height
            ? `${data.width}×${data.height} см`
            : null,

          // Transform images from objects to URLs
          images: Array.isArray(data.images) ? data.images.map(img => img.url) : [],

          // Transform variants to sizes with formatted prices
          sizes: normalizedVariants.map(variant => ({
            id: variant.size.toLowerCase(),
            label: variant.size,
            price: formatPrice(variant.price),
            priceValue: kopecksToTenge(variant.price)
          })),

          // Composition stays the same
          composition: normalizedComposition,

          // Transform addons to additional options with checked state
          additionalOptions: Array.isArray(data.addons) ? data.addons.map(addon => ({
            id: addon.id,
            label: addon.name,
            price: addon.price,
            checked: false
          })) : [],

          // Transform frequently_bought to frequentlyBought
          frequentlyBought: Array.isArray(data.frequently_bought) ? data.frequently_bought.map(item => ({
            id: item.id,
            name: item.name,
            price: formatPrice(item.price),
            priceValue: item.price,
            image: item.image
          })) : [],

          // Pickup addresses stay as strings
          pickupAddresses: Array.isArray(data.pickup_locations) ? data.pickup_locations : [],

          // Description
          description: descriptionText,

          // Transform reviews
          productReviews: {
            count: data.reviews.product.count,
            averageRating: data.reviews.product.average_rating,
            ratingBreakdown: data.reviews.product.breakdown,
            photos: data.reviews.product.photos.map(url => ({ id: Math.random(), url })),
            items: data.reviews.product.items.map(review => ({
              id: review.id,
              author: review.author_name,
              avatar: null,
              date: new Date(review.created_at).toLocaleDateString('ru-RU', {
                day: 'numeric',
                month: 'long',
                year: 'numeric'
              }),
              rating: review.rating,
              text: review.text,
              photos: [],
              likes: review.likes || 0,
              dislikes: review.dislikes || 0
            }))
          },

          companyReviews: {
            count: data.reviews.company.count,
            averageRating: data.reviews.company.average_rating,
            ratingBreakdown: data.reviews.company.breakdown,
            photos: [],
            items: data.reviews.company.items.map(review => ({
              id: review.id,
              author: review.author_name,
              avatar: null,
              date: new Date(review.created_at).toLocaleDateString('ru-RU', {
                day: 'numeric',
                month: 'long',
                year: 'numeric'
              }),
              rating: review.rating,
              text: review.text,
              photos: [],
              likes: review.likes || 0,
              dislikes: review.dislikes || 0
            }))
          }
        };

        setProduct(transformedProduct);
        setAdditionalOptions(transformedProduct.additionalOptions);

        // Set default size to 'm' or first available
        const defaultSize = transformedProduct.sizes.find(s => s.id === 'm')?.id
          || transformedProduct.sizes[0]?.id;
        setSelectedSize(defaultSize);

        setError(null);
      } catch (err) {
        console.error('Failed to load product:', err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }

    if (id) {
      loadProduct();
    }
  }, [id]);

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
    if (!product) return;

    const cartItem = {
      productId: product.id,
      name: product.name,
      image: product.images[0],
      size: product.sizeDescription || '1 шт',
      price: product.mainPrice,
      priceValue: product.mainPriceValue,
      quantity: 1
    };

    addToCart(cartItem);
    navigate('/cart');
  };

  const handleLoadMoreReviews = () => {
    console.log('Load more reviews');
  };

  // Loading state
  if (loading) {
    return (
      <div className="bg-white min-h-screen w-full max-w-sm mx-auto flex items-center justify-center">
        <div className="text-center">
          <div className="text-lg font-sans text-text-black">Загрузка...</div>
        </div>
      </div>
    );
  }

  // Error state
  if (error || !product) {
    return (
      <div className="bg-white min-h-screen w-full max-w-sm mx-auto flex items-center justify-center">
        <div className="text-center px-4">
          <div className="text-lg font-sans text-text-black mb-4">
            {error || 'Товар не найден'}
          </div>
          <CvetyButton onClick={() => navigate('/')}>
            Вернуться на главную
          </CvetyButton>
        </div>
      </div>
    );
  }

  // Get current price based on selected size
  const selectedSizeData = selectedSize
    ? product.sizes.find(s => s.id === selectedSize)
    : null;
  const currentPrice = selectedSizeData?.price || product.mainPrice;

  // Get current reviews based on active tab
  const currentReviews = activeReviewTab === 'product'
    ? product.productReviews
    : product.companyReviews;

  return (
    <div className="bg-white min-h-screen w-full max-w-sm mx-auto flex flex-col">
      <Header cartCount={getCartCount()} />

      <main className="flex-1 px-4 py-6 space-y-6">
          {/* Product Header with Rating */}
          <ProductHeaderWithRating
            name={product.name}
            rating={product.rating}
            reviewCount={product.reviewCount}
            ratingCount={product.ratingCount}
            size={selectedSizeData?.label || product.sizeDescription}
          />

          {/* Product Image Gallery */}
          <ProductImageGallery
            images={product.images}
            alt={product.name}
          />

          {/* Price */}
          <div className="font-sans font-bold text-h1 text-text-black">
            {currentPrice}
          </div>

          {/* Size Selector */}
          {product.sizes.length > 0 && (
            <SizeSelector
              sizes={product.sizes}
              selectedSize={selectedSize}
              onSizeSelect={handleSizeSelect}
            />
          )}

          {/* Composition */}
          {product.composition.length > 0 && (
            <CompositionSection items={product.composition} />
          )}

          {/* Additional Options */}
          <AdditionalOptions
            title="Дополнительно"
            options={additionalOptions}
            onOptionToggle={handleOptionToggle}
          />

          {/* Frequently Bought Together */}
          <FrequentlyBoughtTogether
            products={product.frequentlyBought}
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
            addresses={product.pickupAddresses}
          />

          {/* Description (Expandable) */}
          <ExpandableSection title="Описание" defaultExpanded>
            <p className="font-sans font-normal text-body-2 text-text-black">
              {product.description}
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
              productReviewsCount={product.productReviews.count}
              companyReviewsCount={product.companyReviews.count}
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
