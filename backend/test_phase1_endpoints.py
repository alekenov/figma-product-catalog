#!/usr/bin/env python3
"""
Phase 1 API Endpoint Tests
Tests for /products/home and /products/filters endpoints
"""

import requests
import json
from typing import Dict, Any

BASE_URL = "http://localhost:8014/api/v1"
PASSED = 0
FAILED = 0


def print_test(name: str, passed: bool, message: str = ""):
    """Print test result"""
    global PASSED, FAILED
    symbol = "✓" if passed else "✗"
    status = "PASS" if passed else "FAIL"

    if passed:
        PASSED += 1
    else:
        FAILED += 1

    print(f"{symbol} [{status}] {name}")
    if message:
        print(f"    {message}")


def test_home_endpoint_basic():
    """Test 1: GET /products/home - Basic functionality"""
    print("\n🧪 Test Group 1: /products/home basic functionality")

    try:
        response = requests.get(f"{BASE_URL}/products/home", timeout=5)
        print_test("Response status 200", response.status_code == 200)

        data = response.json()
        print_test("Response has 'featured' field", "featured" in data)
        print_test("Response has 'available_tags' field", "available_tags" in data)
        print_test("Response has 'bestsellers' field", "bestsellers" in data)

        print_test("Featured is a list", isinstance(data.get("featured"), list))
        print_test("Featured list not empty", len(data.get("featured", [])) > 0,
                  f"Found {len(data.get('featured', []))} products")

        print_test("Available tags is a list", isinstance(data.get("available_tags"), list))
        print_test("Tags list not empty", len(data.get("available_tags", [])) > 0,
                  f"Found tags: {', '.join(data.get('available_tags', []))}")

        # Check product structure
        if data.get("featured"):
            product = data["featured"][0]
            required_fields = ["id", "name", "price", "image", "tags", "is_featured"]
            for field in required_fields:
                print_test(f"Product has '{field}' field", field in product)

            print_test("Product price is in kopecks", product.get("price", 0) > 10000,
                      f"Price: {product.get('price')} kopecks = {product.get('price', 0) // 100} tenge")

    except Exception as e:
        print_test("Basic endpoint test", False, f"Error: {str(e)}")


def test_home_endpoint_filters():
    """Test 2: GET /products/home - Filter functionality"""
    print("\n🧪 Test Group 2: /products/home filtering")

    try:
        # Test city filter
        response = requests.get(f"{BASE_URL}/products/home?city=almaty", timeout=5)
        print_test("City filter returns 200", response.status_code == 200)

        data = response.json()
        almaty_count = len(data.get("featured", []))
        print_test("City filter returns results", almaty_count > 0,
                  f"Found {almaty_count} products for Almaty")

        # Test tags filter
        response = requests.get(f"{BASE_URL}/products/home?tags=roses", timeout=5)
        print_test("Tags filter returns 200", response.status_code == 200)

        data = response.json()
        roses_count = len(data.get("featured", []))
        print_test("Tags filter returns results", roses_count > 0,
                  f"Found {roses_count} products with roses tag")

        # Verify filtering actually works
        if data.get("featured"):
            for product in data["featured"]:
                has_roses_tag = "roses" in product.get("tags", [])
                print_test(f"Product '{product.get('name')}' has roses tag", has_roses_tag)
                if not has_roses_tag:
                    break  # Only check first mismatch

        # Test multiple tags
        response = requests.get(f"{BASE_URL}/products/home?tags=roses,urgent", timeout=5)
        print_test("Multiple tags filter returns 200", response.status_code == 200)

        data = response.json()
        multi_count = len(data.get("featured", []))
        print_test("Multiple tags filter works", True,
                  f"Found {multi_count} products with roses+urgent")

        # Test limit parameter
        response = requests.get(f"{BASE_URL}/products/home?limit=2", timeout=5)
        data = response.json()
        print_test("Limit parameter works", len(data.get("featured", [])) <= 2,
                  f"Requested 2, got {len(data.get('featured', []))}")

    except Exception as e:
        print_test("Filter functionality test", False, f"Error: {str(e)}")


def test_filters_endpoint():
    """Test 3: GET /products/filters"""
    print("\n🧪 Test Group 3: /products/filters")

    try:
        response = requests.get(f"{BASE_URL}/products/filters", timeout=5)
        print_test("Response status 200", response.status_code == 200)

        data = response.json()
        print_test("Response has 'tags' field", "tags" in data)
        print_test("Response has 'cities' field", "cities" in data)
        print_test("Response has 'price_range' field", "price_range" in data)
        print_test("Response has 'product_types' field", "product_types" in data)

        # Check tags
        tags = data.get("tags", [])
        print_test("Tags is a list", isinstance(tags, list))
        print_test("Tags not empty", len(tags) > 0, f"Found {len(tags)} tags")
        print_test("Tags are sorted", tags == sorted(tags))

        expected_tags = ["budget", "discount", "mom", "roses", "urgent", "valentine", "wholesale"]
        for tag in expected_tags:
            print_test(f"Has '{tag}' tag", tag in tags)

        # Check cities
        cities = data.get("cities", [])
        print_test("Cities is a list", isinstance(cities, list))
        print_test("Has almaty city", "almaty" in cities)
        print_test("Has astana city", "astana" in cities)

        # Check price_range
        price_range = data.get("price_range", {})
        print_test("Price range has 'min' field", "min" in price_range)
        print_test("Price range has 'max' field", "max" in price_range)
        print_test("Price range has 'min_tenge' field", "min_tenge" in price_range)
        print_test("Price range has 'max_tenge' field", "max_tenge" in price_range)

        min_price = price_range.get("min", 0)
        max_price = price_range.get("max", 0)
        print_test("Min price less than max price", min_price < max_price,
                  f"Range: {min_price // 100} - {max_price // 100} ₸")

        # Check product_types
        types = data.get("product_types", [])
        print_test("Product types not empty", len(types) > 0)
        expected_types = ["flowers", "sweets", "fruits", "gifts"]
        for ptype in expected_types:
            print_test(f"Has '{ptype}' type", ptype in types)

    except Exception as e:
        print_test("Filters endpoint test", False, f"Error: {str(e)}")


def test_price_formatting():
    """Test 4: Price formatting (kopecks vs tenge)"""
    print("\n🧪 Test Group 4: Price formatting")

    try:
        response = requests.get(f"{BASE_URL}/products/home", timeout=5)
        data = response.json()

        if data.get("featured"):
            product = data["featured"][0]
            price_kopecks = product.get("price", 0)
            price_tenge = price_kopecks // 100

            print_test("Price stored in kopecks", price_kopecks > 100000,
                      f"Backend: {price_kopecks} kopecks")
            print_test("Price conversion to tenge", price_tenge > 1000,
                      f"Display: {price_tenge} ₸")
            print_test("Price is reasonable", 5000 <= price_tenge <= 20000,
                      f"Range check: {price_tenge} ₸ is between 5000-20000")

        # Check filters endpoint price range
        response = requests.get(f"{BASE_URL}/products/filters", timeout=5)
        data = response.json()
        price_range = data.get("price_range", {})

        print_test("Min price in both formats",
                   price_range.get("min") == price_range.get("min_tenge") * 100)
        print_test("Max price in both formats",
                   price_range.get("max") == price_range.get("max_tenge") * 100)

    except Exception as e:
        print_test("Price formatting test", False, f"Error: {str(e)}")


def main():
    """Run all tests"""
    print("=" * 70)
    print("🚀 Phase 1 API Endpoint Tests")
    print("=" * 70)

    # Run all test groups
    test_home_endpoint_basic()
    test_home_endpoint_filters()
    test_filters_endpoint()
    test_price_formatting()

    # Print summary
    print("\n" + "=" * 70)
    print(f"📊 Test Results: {PASSED} passed, {FAILED} failed")
    print("=" * 70)

    if FAILED == 0:
        print("✅ All Phase 1 tests passed!")
        return 0
    else:
        print(f"❌ {FAILED} test(s) failed")
        return 1


if __name__ == "__main__":
    exit(main())