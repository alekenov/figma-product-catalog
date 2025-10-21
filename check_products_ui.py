#!/usr/bin/env python3
"""
Проверка товаров в Production API с фотографиями
"""
import requests

print("=" * 80)
print("Товары в магазине shop_id=17008 (Production)")
print("=" * 80)
print()

# Получаем товары
response = requests.get("https://figma-product-catalog-production.up.railway.app/api/v1/products", params={"shop_id": 17008})
products = response.json()

print(f"Всего товаров: {len(products)}")
print()

# Показываем первые 5 товаров с фото
for i, product in enumerate(products[:5], 1):
    print(f"{i}. {product['name']}")
    print(f"   ID: {product['id']}")
    print(f"   Цена: {product['price']/100:.0f}₸")
    print(f"   Фото: {product['image']}")
    print()

# Статистика visual search
print("=" * 80)
print("Статистика Visual Search")
print("=" * 80)
stats_response = requests.get(
    "https://figma-product-catalog-production.up.railway.app/api/v1/products/search/stats",
    params={"shop_id": 17008}
)
stats = stats_response.json()
print(f"Всего товаров: {stats['total_products']}")
print(f"Товаров с embeddings: {stats['products_with_embeddings']}")
print(f"Покрытие: {stats['coverage_percentage']}%")
print(f"Готовность к поиску: {'✅ Да' if stats['search_ready'] else '❌ Нет'}")
print()

# Тестируем visual search
print("=" * 80)
print("Тест Visual Search: поиск похожих на Кустовые розы")
print("=" * 80)
search_response = requests.post(
    "https://figma-product-catalog-production.up.railway.app/api/v1/products/search/similar",
    json={
        "image_url": "https://cvety.kz/upload/resize_cache/iblock/a97/xz49vqgvoeshj87kyqdsori263robezf/435_545_2/IMG_0021.jpeg",
        "shop_id": 17008,
        "limit": 3
    }
)
results = search_response.json()

if 'results' in results:
    print(f"Найдено: {len(results['results'])} товаров")
    print()
    for i, product in enumerate(results['results'], 1):
        print(f"{i}. {product['name']} - {product.get('similarity', 0):.3f} similarity")
        print(f"   ID: {product['id']}, Цена: {product['price']/100:.0f}₸")
        print(f"   Фото: {product['image']}")
        print()
else:
    print("Ошибка поиска:", results)
    print()
