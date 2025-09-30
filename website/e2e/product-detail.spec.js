/**
 * Product Detail Page Tests
 *
 * Ensures bouquet details show composition, dimensions and description.
 */
import { test, expect } from '@playwright/test';

const productDetailResponse = {
  id: 4,
  name: 'Тестовый букет',
  price: 1500000,
  type: 'flowers',
  description: 'Описание букета для проверки отображения деталей.',
  image: 'https://example.com/test-bouquet.jpg',
  enabled: true,
  is_featured: true,
  colors: ['pink'],
  occasions: ['romantic'],
  cities: ['almaty'],
  tags: ['test'],
  manufacturingTime: 45,
  width: 35,
  height: 30,
  shelfLife: 7,
  rating: 4.8,
  review_count: 12,
  rating_count: 20,
  images: [
    {
      product_id: 4,
      url: 'https://example.com/test-bouquet.jpg',
      order: 0,
      is_primary: true,
      id: 700,
      created_at: '2024-01-01T10:00:00'
    }
  ],
  variants: [],
  composition: [
    { id: 1, name: 'Роза красная', quantity: 15 },
    { id: 2, name: 'Эвкалипт', quantity: 5 }
  ],
  addons: [],
  frequently_bought: [],
  pickup_locations: ['ул. Абая, 10'],
  reviews: {
    product: {
      count: 2,
      average_rating: 4.5,
      breakdown: { '5': 1, '4': 1, '3': 0, '2': 0, '1': 0 },
      photos: [],
      items: [
        {
          id: 1,
          author_name: 'Анна',
          rating: 5,
          text: 'Очень красивый букет!',
          created_at: '2024-01-02T12:00:00'
        }
      ]
    },
    company: {
      count: 1,
      average_rating: 5,
      breakdown: { '5': 1, '4': 0, '3': 0, '2': 0, '1': 0 },
      photos: [],
      items: [
        {
          id: 2,
          author_name: 'Иван',
          rating: 5,
          text: 'Отличный сервис!',
          created_at: '2024-01-03T12:00:00'
        }
      ]
    }
  }
};

// Extend review items with optional fields the UI expects
productDetailResponse.reviews.product.items = productDetailResponse.reviews.product.items.map(item => ({
  likes: 0,
  dislikes: 0,
  photos: [],
  ...item
}));

productDetailResponse.reviews.company.items = productDetailResponse.reviews.company.items.map(item => ({
  likes: 0,
  dislikes: 0,
  photos: [],
  ...item
}));

test.describe('Product Detail Page', () => {
  test('shows composition, description and size information', async ({ page }) => {
    await page.route('**/api/v1/products/4/detail', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(productDetailResponse)
      });
    });

    await page.goto('/product/4');

    await expect(page.getByRole('heading', { level: 1, name: 'Тестовый букет' })).toBeVisible();

    await expect(page.getByText('35×30 см')).toBeVisible();

    await expect(page.getByRole('heading', { name: 'Состав' })).toBeVisible();
    await expect(page.getByText('Роза красная')).toBeVisible();
    await expect(page.getByText('15 шт.')).toBeVisible();

    await expect(page.getByText('Описание букета для проверки отображения деталей.', { exact: false })).toBeVisible();
  });
});
