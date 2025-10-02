#!/usr/bin/env python3
"""
Bulk Upload Products Script for Cvety.kz
Uploads flower bouquets from photos with auto-generated data
"""
import json
import requests
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional

# Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8014/api/v1")
IMAGE_WORKER_URL = "https://flower-shop-images.alekenov.workers.dev"
PHOTOS_DIR = "/Users/alekenov/Downloads/demo"
PRODUCTS_DATA_FILE = Path(__file__).parent / "products_data.json"

# ANSI color codes for terminal output
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'


def load_products_data() -> List[Dict]:
    """Load product data from JSON file"""
    try:
        with open(PRODUCTS_DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"{RED}❌ Error: products_data.json not found at {PRODUCTS_DATA_FILE}{RESET}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"{RED}❌ Error parsing JSON: {e}{RESET}")
        sys.exit(1)


def upload_image_to_r2(image_path: str) -> Optional[str]:
    """
    Upload image to Cloudflare R2 via Cloudflare Worker
    Returns: R2 URL or None if failed
    """
    endpoint = f"{IMAGE_WORKER_URL}/upload"

    try:
        with open(image_path, 'rb') as f:
            files = {'file': (Path(image_path).name, f, 'image/jpeg')}
            response = requests.post(endpoint, files=files, timeout=30)

        if response.status_code == 201 or response.status_code == 200:
            data = response.json()
            # Worker returns {url: "https://..."} or {success: true, url: "..."}
            return data.get('url') or data.get('imageUrl')
        else:
            print(f"{YELLOW}⚠️  Image upload failed: HTTP {response.status_code}{RESET}")
            try:
                error_data = response.json()
                print(f"       Error: {error_data.get('error', 'Unknown error')}")
            except:
                pass
            return None

    except requests.exceptions.RequestException as e:
        print(f"{RED}❌ Network error uploading image: {e}{RESET}")
        return None
    except Exception as e:
        print(f"{RED}❌ Unexpected error uploading image: {e}{RESET}")
        return None


def create_product(product_data: Dict, image_url: str) -> Optional[int]:
    """
    Create product via backend API
    Returns: Product ID or None if failed
    """
    endpoint = f"{API_BASE_URL}/products"

    # Prepare payload matching backend ProductCreate schema
    payload = {
        "name": product_data["name"],
        "price": product_data["price"],  # Already in kopecks
        "type": product_data["type"],
        "description": product_data["description"],
        "image": image_url,
        "enabled": product_data.get("enabled", True),
        "is_featured": product_data.get("is_featured", False),
        "colors": product_data.get("colors", []),
        "occasions": product_data.get("occasions", []),
        "cities": product_data.get("cities", []),
        "tags": product_data.get("tags", []),
        "manufacturingTime": product_data.get("manufacturing_time"),
        "shelfLife": product_data.get("shelf_life")
    }

    try:
        response = requests.post(
            endpoint,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )

        if response.status_code == 200 or response.status_code == 201:
            data = response.json()
            return data.get('id')
        else:
            print(f"{YELLOW}⚠️  Product creation failed: HTTP {response.status_code}{RESET}")
            print(f"Response: {response.text}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"{RED}❌ Network error creating product: {e}{RESET}")
        return None
    except Exception as e:
        print(f"{RED}❌ Unexpected error creating product: {e}{RESET}")
        return None


def format_price(kopecks: int) -> str:
    """Format price in kopecks to tenge string"""
    tenge = kopecks // 100
    return f"{tenge:,}₸".replace(',', ' ')


def upload_single_product(product_data: Dict, index: int, total: int) -> bool:
    """Upload a single product with its image"""

    filename = product_data.get("filename")
    name = product_data.get("name")
    price = product_data.get("price", 0)

    # Check if we should skip this product
    if product_data.get("skip_upload"):
        print(f"{YELLOW}⏭️  Букет {index}/{total}: '{name}' пропущен (дубликат){RESET}")
        return True

    print(f"\n{BOLD}{BLUE}📸 Букет {index}/{total}: {name}{RESET}")
    print(f"   Цена: {format_price(price)}")

    # Find image file
    image_path = Path(PHOTOS_DIR) / filename
    if not image_path.exists():
        print(f"{RED}❌ Фото не найдено: {image_path}{RESET}")
        return False

    # Step 1: Upload image
    print(f"   ⬆️  Загружаю фото в R2...")
    image_url = upload_image_to_r2(str(image_path))
    if not image_url:
        print(f"{RED}❌ Не удалось загрузить фото{RESET}")
        return False

    print(f"   {GREEN}✓{RESET} Фото загружено: {image_url[:60]}...")

    # Step 2: Create product
    print(f"   📝 Создаю товар в каталоге...")
    product_id = create_product(product_data, image_url)
    if not product_id:
        print(f"{RED}❌ Не удалось создать товар{RESET}")
        return False

    print(f"   {GREEN}✅ Товар создан! ID: {product_id}{RESET}")
    return True


def main():
    """Main execution function"""
    print(f"\n{BOLD}🌸 Bulk Upload Products to Cvety.kz{RESET}")
    print(f"{'=' * 50}\n")

    # Load products data
    print(f"📂 Загружаю данные из {PRODUCTS_DATA_FILE.name}...")
    products = load_products_data()
    print(f"   {GREEN}✓{RESET} Найдено {len(products)} букетов\n")

    # Check photos directory
    if not Path(PHOTOS_DIR).exists():
        print(f"{RED}❌ Директория с фото не найдена: {PHOTOS_DIR}{RESET}")
        sys.exit(1)

    # Check backend availability
    print(f"🔍 Проверяю подключение к backend...")
    try:
        response = requests.get(f"{API_BASE_URL}/../health", timeout=5)
        if response.status_code == 200:
            print(f"   {GREEN}✓{RESET} Backend доступен: {API_BASE_URL}\n")
        else:
            print(f"{YELLOW}⚠️  Backend вернул статус {response.status_code}{RESET}\n")
    except requests.exceptions.RequestException:
        print(f"{RED}❌ Backend недоступен! Убедитесь что он запущен на {API_BASE_URL}{RESET}")
        print(f"   Запустите: cd backend && python3 main.py\n")
        sys.exit(1)

    # Upload products
    successful = 0
    failed = 0
    skipped = 0

    for index, product in enumerate(products, start=1):
        if product.get("skip_upload"):
            skipped += 1
            continue

        success = upload_single_product(product, index, len(products))
        if success:
            successful += 1
        else:
            failed += 1

    # Summary
    print(f"\n{BOLD}{'=' * 50}{RESET}")
    print(f"{BOLD}📊 Результаты загрузки:{RESET}\n")
    print(f"   {GREEN}✅ Успешно:{RESET} {successful}")
    print(f"   {RED}❌ Ошибки:{RESET} {failed}")
    print(f"   {YELLOW}⏭️  Пропущено:{RESET} {skipped}")
    print(f"\n{BOLD}🎉 Загрузка завершена!{RESET}\n")

    if failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{YELLOW}⚠️  Загрузка прервана пользователем{RESET}\n")
        sys.exit(130)
    except Exception as e:
        print(f"\n{RED}❌ Критическая ошибка: {e}{RESET}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)
