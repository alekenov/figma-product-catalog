# API Testing Guide

Comprehensive guide for testing all 147 API endpoints in the figma-product-catalog backend.

## Quick Start

```bash
# Navigate to backend directory
cd /Users/alekenov/figma-product-catalog/backend

# Run all tests with default configuration
./test_api_endpoints.sh

# Run with custom configuration
API_BASE=http://localhost:8014/api/v1 \
TEST_PHONE=77015211545 \
TEST_PASSWORD=1234 \
SHOP_ID=8 \
./test_api_endpoints.sh
```

## Prerequisites

1. **Backend server must be running** on port 8014:
   ```bash
   python3 main.py
   ```

2. **Required tools**:
   - `curl` - HTTP client
   - `jq` - JSON processor for parsing responses

3. **Test credentials**:
   - Phone: `77015211545`
   - Password: `1234`
   - This account should have DIRECTOR role with shop_id=8

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `API_BASE` | `http://localhost:8014/api/v1` | Base API URL |
| `TEST_PHONE` | `77015211545` | Test account phone |
| `TEST_PASSWORD` | `1234` | Test account password |
| `SHOP_ID` | `8` | Shop ID for multi-tenancy tests |

## Test Coverage

### 1. Authentication (7 endpoints)
- ✅ Login/Logout
- ✅ Token refresh and verification
- ✅ User registration (skipped to avoid test data)
- ✅ Password change (skipped to avoid test data)

### 2. Products (20 endpoints)
- ✅ Public product listing and search
- ✅ Homepage products with filters
- ✅ Product detail views
- ✅ Availability checking
- ✅ Admin CRUD operations (read-only tests)

### 3. Orders (31 endpoints)
- ✅ Order listing and filtering
- ✅ Order tracking by tracking_id (public)
- ✅ Order CRUD operations
- ✅ Status management and history
- ✅ Item reservation system
- ✅ Photo upload/feedback

### 4. Warehouse (14 endpoints)
- ✅ Inventory item management
- ✅ Stock operations (delivery, sale, writeoff)
- ✅ Operation history tracking

### 5. Recipes (8 endpoints)
- ✅ Product composition (bill of materials)
- ✅ Availability calculations
- ✅ Recipe CRUD operations

### 6. Inventory (11 endpoints)
- ✅ Inventory checks and audits
- ✅ Reservation system
- ✅ Stock validation
- ✅ Expired reservation cleanup

### 7. Clients (9 endpoints)
- ✅ Client CRM functionality
- ✅ Order history per client
- ✅ Client statistics
- ✅ Phone normalization

### 8. Shop Settings (7 endpoints)
- ✅ Public shop info (no auth)
- ✅ Working hours configuration
- ✅ Delivery cost calculation
- ✅ Multi-tenancy validation

### 9. User Profile & Team (12 endpoints)
- ✅ User profile management
- ✅ Team member listing
- ✅ Role-based access
- ✅ Invitation system

### 10. Reviews (6 endpoints)
- ✅ Company reviews
- ✅ Product reviews
- ✅ Review photos

### 11. Content/CMS (8 endpoints)
- ✅ FAQ management
- ✅ Static pages

### 12. Superadmin (14 endpoints)
- ✅ Platform-wide shop management
- ✅ Cross-shop user management
- ✅ Platform statistics
- ⚠️ Requires `is_superadmin=True` on user account

## Output Format

The script provides color-coded output:

- 🔵 **Blue**: Section headers
- 🟡 **Yellow**: Test execution
- 🟢 **Green**: Passed tests
- 🔴 **Red**: Failed tests

Example output:
```
═══════════════════════════════════════════════════════════
  1. Authentication Endpoints
═══════════════════════════════════════════════════════════

Testing: POST /auth/login - Login with credentials
✓ PASSED: POST /auth/login
  Response: {"access_token":"eyJ...","token_type":"bearer"}

Testing: GET /auth/me - Get current user info
✓ PASSED: GET /auth/me
  Response: {"id":13,"name":"Test Owner","role":"DIRECTOR"}
```

## Exit Codes

- `0`: All tests passed
- `1`: One or more tests failed

## Test Categories

### Public Endpoints (No Authentication)
Tests that don't require JWT token:
```bash
# Product listings
GET /products/?shop_id={id}
GET /products/home?shop_id={id}

# Order tracking
GET /orders/by-tracking/{tracking_id}/status

# Reviews
GET /reviews/company
GET /reviews/product/{id}

# Shop info
GET /shop/settings/public?shop_id={id}
```

### Authenticated Endpoints (Requires Token)
Tests that require valid JWT:
```bash
# All CRUD operations
POST /products/
PUT /products/{id}
DELETE /products/{id}

# Admin operations
GET /orders/
PATCH /orders/{id}/status

# User management
GET /profile/team
POST /profile/team/invite
```

### Role-Based Endpoints
Tests that require specific roles:
```bash
# DIRECTOR only
PUT /shop/settings
PUT /shop/working-hours

# MANAGER or DIRECTOR
POST /profile/team/invite
DELETE /profile/team/{id}

# SUPERADMIN only
GET /superadmin/shops
PUT /superadmin/shops/{id}/block
```

## Multi-Tenancy Testing

All authenticated endpoints are automatically filtered by `shop_id` from JWT:

```bash
# This request will only return products for the authenticated user's shop
GET /products/admin
Authorization: Bearer {token_with_shop_id_8}

# Response will only include products where product.shop_id = 8
```

To test multi-tenancy isolation:
1. Create two test users in different shops
2. Login with User A (shop_id=8)
3. Attempt to access User B's resources (shop_id=9)
4. Should receive 403 Forbidden or 404 Not Found

## Common Issues

### Issue: "Failed to get authentication token"
**Solution**: Verify backend is running and credentials are correct
```bash
# Check backend status
curl http://localhost:8014/health

# Verify credentials
psql -d flower_shop -c "SELECT * FROM user WHERE phone='77015211545';"
```

### Issue: "command not found: jq"
**Solution**: Install jq JSON processor
```bash
# macOS
brew install jq

# Ubuntu/Debian
sudo apt-get install jq
```

### Issue: "Connection refused"
**Solution**: Start backend server
```bash
cd /Users/alekenov/figma-product-catalog/backend
python3 main.py
```

### Issue: Many tests failing with 403 Forbidden
**Solution**: Check if test account has proper role and shop_id
```bash
# Should be DIRECTOR with active shop
SELECT u.*, s.* FROM user u
LEFT JOIN shop s ON u.shop_id = s.id
WHERE u.phone='77015211545';
```

## Manual Testing Examples

### Test Authentication Flow
```bash
# 1. Login
curl -X POST http://localhost:8014/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"phone":"77015211545","password":"1234"}' \
  | jq '.'

# 2. Save token
TOKEN="eyJ..."

# 3. Use token for protected endpoint
curl -X GET http://localhost:8014/api/v1/auth/me \
  -H "Authorization: Bearer $TOKEN" \
  | jq '.'
```

### Test Order Creation Flow
```bash
# 1. Check product availability
curl -X POST http://localhost:8014/api/v1/orders/check-availability \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '[{"product_id":1,"quantity":2}]' \
  | jq '.'

# 2. Preview cart
curl -X POST http://localhost:8014/api/v1/orders/preview \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '[{"product_id":1,"quantity":2}]' \
  | jq '.'

# 3. Create order with items
curl -X POST http://localhost:8014/api/v1/orders/with-items \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "customerName":"Test Customer",
    "phone":"77001234567",
    "items":[{"product_id":1,"quantity":2}],
    "check_availability":true
  }' \
  | jq '.'
```

### Test Public Order Tracking
```bash
# Track order by tracking ID (no auth required)
curl -X GET http://localhost:8014/api/v1/orders/by-tracking/123456789/status \
  | jq '.'
```

## Integration with CI/CD

### GitHub Actions Example
```yaml
name: API Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:14
        env:
          POSTGRES_DB: flower_shop_test
          POSTGRES_PASSWORD: postgres
    steps:
      - uses: actions/checkout@v2

      - name: Install dependencies
        run: |
          pip install -r backend/requirements.txt
          sudo apt-get install -y jq

      - name: Start backend
        run: |
          cd backend
          python main.py &
          sleep 5

      - name: Run API tests
        run: |
          cd backend
          chmod +x test_api_endpoints.sh
          ./test_api_endpoints.sh
```

## Performance Testing

For load testing, use tools like:

### Apache Bench (ab)
```bash
# Test product listing endpoint
ab -n 1000 -c 10 \
  "http://localhost:8014/api/v1/products/?shop_id=8"
```

### wrk (recommended for high load)
```bash
# Install wrk
brew install wrk  # macOS

# Test with authentication
wrk -t4 -c100 -d30s \
  -H "Authorization: Bearer $TOKEN" \
  http://localhost:8014/api/v1/orders/
```

## Next Steps

1. **Add pytest tests** for more detailed unit/integration testing
2. **Create Postman/Insomnia collection** for manual testing
3. **Setup continuous monitoring** with health checks
4. **Add performance benchmarks** for critical endpoints

## Contributing

When adding new endpoints:

1. Update this guide with new endpoint documentation
2. Add corresponding test to `test_api_endpoints.sh`
3. Ensure multi-tenancy validation if applicable
4. Update TOTAL_TESTS counter in script

## References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [curl Manual](https://curl.se/docs/manual.html)
- [jq Manual](https://stedolan.github.io/jq/manual/)
- [Backend API Structure](/Users/alekenov/figma-product-catalog/backend/api/)
