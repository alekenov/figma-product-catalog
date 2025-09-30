# Mock Data Audit - Website Frontend

This document tracks all hardcoded mock data in the website that needs to be replaced with API calls.

## **Current Mock Data Locations**

### 1. HomePage (`/website/src/pages/HomePage.jsx`)
**Lines:** 14-44
**Data:** Product cards for catalog
```javascript
const mockProducts = [
  {
    id: 1,
    image: "...",
    price: "7 900 ₸",
    name: "Розовые розы с оформлением",
    deliveryText: "Доставим завтра к 15:30"
  },
  // ... 3 more products
];
```
**Replacement:** `GET /api/v1/products/home?city=Astana`

**Filter Tags:** Lines 47-57
```javascript
const filterTags = [
  { id: 'urgent', label: 'Срочно', icon: <FilterIcons.Lightning /> },
  // ... more tags
];
```
**Replacement:** `GET /api/v1/products/filters`

---

### 2. ProductDetailPage (`/website/src/pages/ProductDetailPage.jsx`)
**Lines:** 18-160
**Data:** Complete product details
```javascript
const mockProduct = {
  id: 1,
  name: "Букет розовых пионов",
  rating: 4.8,
  reviewCount: 58,
  mainPrice: "22 500 ₸",
  images: [...],
  sizes: [{id: 's', label: 'S', price: '15 000 ₸'}, ...],
  composition: [...],
  additionalOptions: [...],
  frequentlyBought: [...],
  pickupAddresses: [...],
  description: "...",
  productReviews: {...},
  companyReviews: {...}
};
```
**Replacement:** `GET /api/v1/products/{id}/detail`

---

### 3. CartPage (`/website/src/pages/CartPage.jsx`)
**Lines:** 18-46
**Data:** Cart items (currently using CartContext with localStorage)
```javascript
const mockCartItems = [
  {
    id: 1,
    image: "...",
    name: "Комбобукет",
    size: "L",
    price: "6 900 ₸",
    priceValue: 6900,
    quantity: 1
  },
  // ... 2 more items
];
```
**Replacement:**
- Keep CartContext for anonymous users (localStorage)
- Add optional sync to backend for authenticated users

---

### 4. OrderStatusPage (`/website/src/pages/OrderStatusPage.jsx`)
**Lines:** 48-80
**Data:** Order details and status
```javascript
return {
  orderId: '70834',
  status: 'delivering', // confirmed | preparing | delivering
  recipient: {name: 'Ксения', phone: '+7 (917) 096-5427'},
  pickupAddress: '...',
  deliveryAddress: '...',
  dateTime: '...',
  sender: {phone: '...'},
  photos: [...],
  items: [...],
  deliveryCost: 0,
  deliveryType: 'Самовывоз',
  total: 43500,
  bonusPoints: 985
};
```
**Replacement:** `GET /api/v1/orders/track/{order_number}`

---

## **Shared Mock Data**

### FAQSection (`/website/src/components/FAQSection.jsx`)
**Lines:** 5-46
**Data:** FAQ questions and answers
```javascript
const mockFAQs = [
  {
    id: 1,
    question: "Почему заказывать цветы в Астане стоит в Cvety.kz?",
    answer: "..."
  },
  // ... 7 more questions
];
```
**Replacement:** `GET /api/v1/faq`

---

### ReviewsSection (`/website/src/components/ReviewsSection.jsx`)
**Lines:** Check file for mock reviews
**Replacement:** `GET /api/v1/reviews/company?limit=20`

---

## **Migration Strategy**

### Phase 1: Core Catalog (Priority 1)
1. ✅ HomePage product cards
2. ✅ Filter tags
3. ProductDetailPage basic info

### Phase 2: Product Details (Priority 2)
4. Composition section
5. Additional options
6. Frequently bought together
7. Pickup locations

### Phase 3: Reviews & Content (Priority 3)
8. Product reviews
9. Company reviews
10. FAQ section

### Phase 4: Cart & Orders (Priority 4)
11. Cart persistence
12. Order creation
13. Order tracking

---

## **Price Format Convention**

**Backend (Database & API):**
- Storage: Kopecks (integers)
- Example: `12000 * 100 = 1200000` kopecks = 12,000 tenge

**Frontend (Display):**
- Display: Tenge with formatting
- Example: `"12 000 ₸"`
- Use utility: `formatPrice(kopecks) => "12 000 ₸"`

---

## **Testing Checklist**

After replacing each mock:
- [ ] API returns expected data structure
- [ ] Prices display correctly (kopecks → tenge)
- [ ] Loading states work
- [ ] Error handling displays properly
- [ ] No console errors
- [ ] UI matches design
- [ ] Performance acceptable