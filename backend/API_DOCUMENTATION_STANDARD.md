# API Documentation Standard

This document defines the standard for documenting API endpoints in the flower shop platform.

**Purpose**: Ensure consistent, comprehensive API documentation across all endpoints
**Last Updated**: 2025-10-28

---

## Docstring Template

Every API endpoint should follow this template:

```python
@router.post("/resource")
async def endpoint_name(
    param: Type,
    current_user: User = Depends(get_current_user)
):
    """
    Brief one-line description of what this endpoint does.

    **Longer Description** (optional):
    Additional context, use cases, or important notes about the endpoint behavior.
    Explain any complex logic or business rules.

    **Authentication**: Required/Optional
    - JWT token required in Authorization header
    - User must have DIRECTOR/MANAGER/WORKER role
    - Shop access controlled via shop_id in JWT

    **Parameters**:
    - param_name (type): Description of what this parameter does
    - optional_param (type, optional): Description (default: value)

    **Request Body** (for POST/PUT/PATCH):
    ```json
    {
      "field1": "value",
      "field2": 123
    }
    ```

    **Response** (200 OK):
    ```json
    {
      "id": 1,
      "status": "success",
      "data": {...}
    }
    ```

    **Error Responses**:
    - 400 Bad Request: Invalid input parameters
    - 401 Unauthorized: Missing or invalid JWT token
    - 403 Forbidden: User doesn't have access to this shop_id
    - 404 Not Found: Resource not found
    - 500 Internal Server Error: Server error

    **Example Usage**:
    ```bash
    curl -X POST http://localhost:8014/api/v1/resource \\
      -H "Authorization: Bearer YOUR_TOKEN" \\
      -H "Content-Type: application/json" \\
      -d '{"field1": "value"}'
    ```

    **Notes**:
    - Any important caveats or edge cases
    - Performance considerations
    - Related endpoints
    """
    # Implementation...
```

---

## Documentation Guidelines

### 1. Brief Description (Required)

First line should be a clear, concise description (one sentence):

✅ **Good**:
```python
"""Get all products for the current shop with optional filtering."""
```

❌ **Bad**:
```python
"""This function retrieves products."""  # Too vague
```

### 2. Authentication Section (Required for Protected Endpoints)

Always specify:
- If JWT token is required
- What roles can access this endpoint
- How shop_id filtering works

Example:
```python
"""
**Authentication**: Required
- JWT token in Authorization: Bearer <token>
- Accessible by: DIRECTOR, MANAGER
- Returns data filtered by user's shop_id
"""
```

### 3. Parameters Section (Required if Parameters Exist)

Document all parameters:

```python
"""
**Parameters**:
- shop_id (int): Shop identifier (required for public endpoints)
- limit (int, optional): Maximum number of results (default: 20, max: 100)
- offset (int, optional): Number of results to skip (default: 0)
- search (str, optional): Search term for product name/description
- enabled_only (bool, optional): Filter enabled products only (default: true)
"""
```

### 4. Request/Response Examples (Required)

Always include:
- Request body format (for POST/PUT/PATCH)
- Success response example
- Error response examples

```python
"""
**Request Body**:
```json
{
  "name": "Red Roses Bouquet",
  "price": 150000,  // Kopecks (1,500 tenge)
  "type": "BOUQUET",
  "enabled": true
}
```

**Response** (201 Created):
```json
{
  "id": 42,
  "name": "Red Roses Bouquet",
  "price": 150000,
  "shop_id": 8,
  "created_at": "2025-10-28T10:00:00Z"
}
```
"""
```

### 5. Error Responses (Required)

Document all possible error codes:

```python
"""
**Error Responses**:
- 400 Bad Request:
  - Price must be positive integer
  - Product name required
  - Invalid product type (must be: BOUQUET, COMPOSITION, SINGLE_FLOWER, ADDITION)
- 401 Unauthorized: Missing or expired JWT token
- 403 Forbidden: User doesn't have permission to create products
- 409 Conflict: Product with this name already exists
- 500 Internal Server Error: Database connection failed
"""
```

### 6. Example Usage (Required for Complex Endpoints)

Provide curl examples:

```python
"""
**Example Usage**:

# Get all products
curl "http://localhost:8014/api/v1/products/?shop_id=8"

# Search products
curl "http://localhost:8014/api/v1/products/?shop_id=8&search=roses&limit=10"

# Create product (authenticated)
curl -X POST http://localhost:8014/api/v1/products/ \\
  -H "Authorization: Bearer $TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{
    "name": "Red Roses",
    "price": 150000,
    "type": "BOUQUET"
  }'
"""
```

### 7. Notes Section (Optional but Recommended)

Add important context:

```python
"""
**Notes**:
- Prices are stored in kopecks (100 kopecks = 1 tenge)
- Phone numbers stored without +7 prefix (77012345678)
- Products are soft-deleted (enabled=false) not physically removed
- Visual search re-indexes products automatically on image update
- Related endpoints: GET /products/{id}, DELETE /products/{id}
"""
```

---

## Common Patterns

### Multi-Tenancy Pattern

All endpoints must respect shop_id isolation:

```python
"""
**Multi-Tenancy**:
This endpoint automatically filters results by the authenticated user's shop_id.
No cross-shop data access is possible.

Example:
- User A (shop_id=8) cannot see User B's data (shop_id=17008)
- JWT token contains shop_id claim
- All database queries filter by shop_id
"""
```

### Pagination Pattern

For list endpoints:

```python
"""
**Pagination**:
- limit (int, optional): Items per page (default: 20, max: 100)
- offset (int, optional): Number of items to skip (default: 0)

Response includes:
```json
{
  "items": [...],
  "total": 150,
  "limit": 20,
  "offset": 0,
  "has_more": true
}
```
"""
```

### Search Pattern

For searchable endpoints:

```python
"""
**Search**:
- search (str, optional): Search term applied to:
  - Product name (case-insensitive)
  - Product description
  - Product tags

Example:
?search=roses        // Finds "Red Roses", "White roses bouquet"
?search=wedding      // Finds products tagged with "wedding"
"""
```

### Filter Pattern

For filterable endpoints:

```python
"""
**Filters**:
- type (str, optional): Product type (BOUQUET, COMPOSITION, SINGLE_FLOWER, ADDITION)
- min_price (int, optional): Minimum price in kopecks
- max_price (int, optional): Maximum price in kopecks
- enabled_only (bool, optional): Show only enabled products (default: true)

Example:
?type=BOUQUET&min_price=100000&max_price=200000
// Finds bouquets between 1,000 and 2,000 tenge
"""
```

---

## FastAPI Integration

FastAPI auto-generates documentation from docstrings. Follow these rules:

### 1. Use Pydantic Models for Request/Response

```python
from pydantic import BaseModel, Field

class ProductCreate(BaseModel):
    """Product creation request"""
    name: str = Field(..., description="Product name", min_length=1, max_length=200)
    price: int = Field(..., description="Price in kopecks", gt=0)
    type: ProductType = Field(..., description="Product type enum")
```

### 2. Add Response Model

```python
@router.post("/products/", response_model=ProductResponse, status_code=201)
async def create_product(product: ProductCreate):
    """Create new product"""
    ...
```

### 3. Document Status Codes

```python
@router.get(
    "/products/{id}",
    response_model=ProductResponse,
    responses={
        404: {"description": "Product not found"},
        403: {"description": "Access denied to this shop"}
    }
)
async def get_product(id: int):
    """Get product by ID"""
    ...
```

---

## Examples of Well-Documented Endpoints

### Example 1: Authentication Endpoint

```python
@router.post("/auth/login", response_model=TokenResponse)
async def login(credentials: LoginRequest):
    """
    Authenticate user and generate JWT token.

    **Authentication Flow**:
    1. Normalize phone number (remove +7 prefix → 77012345678)
    2. Verify phone + password against database
    3. Generate JWT with claims: user_id, phone, role, shop_id
    4. Return access_token with 7-day expiry

    **Authentication**: Public endpoint (no token required)

    **Request Body**:
    ```json
    {
      "phone": "77015211545",     // or "+77015211545"
      "password": "password123"
    }
    ```

    **Response** (200 OK):
    ```json
    {
      "access_token": "eyJhbGc...",
      "token_type": "bearer",
      "user": {
        "id": 13,
        "phone": "77015211545",
        "role": "DIRECTOR",
        "shop_id": 8
      }
    }
    ```

    **Error Responses**:
    - 400 Bad Request: Invalid phone number format
    - 401 Unauthorized: Invalid credentials

    **Example Usage**:
    ```bash
    curl -X POST http://localhost:8014/api/v1/auth/login \\
      -H "Content-Type: application/json" \\
      -d '{"phone": "77015211545", "password": "1234"}'
    ```

    **Notes**:
    - Phone stored without +7 prefix in database
    - JWT expires after 7 days
    - Token includes shop_id for multi-tenancy
    """
```

### Example 2: List Endpoint with Filters

```python
@router.get("/products/", response_model=List[ProductResponse])
async def list_products(
    shop_id: int = Query(..., description="Shop identifier"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    offset: int = Query(0, ge=0, description="Items to skip"),
    search: Optional[str] = Query(None, description="Search term"),
    type: Optional[ProductType] = Query(None, description="Product type filter"),
    enabled_only: bool = Query(True, description="Show enabled products only")
):
    """
    Get paginated list of products with optional filtering.

    **Authentication**: Public endpoint (requires shop_id parameter)

    **Parameters**:
    - shop_id (int): Shop identifier (required)
    - limit (int, optional): Results per page (default: 20, max: 100)
    - offset (int, optional): Skip N results (default: 0)
    - search (str, optional): Search in name/description
    - type (ProductType, optional): Filter by type (BOUQUET, COMPOSITION, etc.)
    - enabled_only (bool, optional): Show only enabled products (default: true)

    **Response** (200 OK):
    ```json
    [
      {
        "id": 1,
        "name": "Red Roses Bouquet",
        "price": 150000,
        "type": "BOUQUET",
        "enabled": true,
        "shop_id": 8,
        "image": "https://..."
      }
    ]
    ```

    **Error Responses**:
    - 400 Bad Request: Invalid shop_id or parameters
    - 500 Internal Server Error: Database query failed

    **Example Usage**:
    ```bash
    # Get all products
    curl "http://localhost:8014/api/v1/products/?shop_id=8"

    # Search roses
    curl "http://localhost:8014/api/v1/products/?shop_id=8&search=roses"

    # Filter by type and price
    curl "http://localhost:8014/api/v1/products/?shop_id=8&type=BOUQUET&limit=10"
    ```

    **Notes**:
    - Results ordered by created_at DESC
    - Image URLs point to Cloudflare R2 CDN
    - Prices in kopecks (divide by 100 for tenge)
    """
```

---

## Quality Checklist

Before committing, verify your endpoint documentation includes:

- [ ] Brief one-line description
- [ ] Authentication requirements (if applicable)
- [ ] All parameters documented with types and defaults
- [ ] Request body example (for POST/PUT/PATCH)
- [ ] Success response example with status code
- [ ] All possible error responses (400, 401, 403, 404, 500)
- [ ] curl command example
- [ ] Notes about multi-tenancy, prices, phone format (if applicable)
- [ ] Related endpoints mentioned

---

## Documentation Review Process

1. **Write docstring** using template above
2. **Test in Swagger UI**: http://localhost:8014/docs
3. **Verify examples work**: Copy curl commands and test
4. **Review with team**: Get feedback on clarity
5. **Update as needed**: Keep docs in sync with code

---

## Maintenance

**When to update documentation:**
- Adding new endpoint
- Changing endpoint behavior
- Adding/removing parameters
- Changing response format
- Fixing bugs that affect API contract

**How to update:**
1. Update docstring in code
2. Test changes locally
3. Verify Swagger UI reflects changes
4. Commit with clear message: `docs: Update X endpoint documentation`

---

## Tools and Resources

**View Generated Docs:**
- Swagger UI: http://localhost:8014/docs
- ReDoc: http://localhost:8014/redoc

**FastAPI Docs:**
- https://fastapi.tiangolo.com/tutorial/path-operation-configuration/
- https://fastapi.tiangolo.com/advanced/additional-responses/

**Pydantic Docs:**
- https://docs.pydantic.dev/latest/

---

**Last Updated**: 2025-10-28
**Maintained by**: Development Team
