# 🚀 Phase 3: ApiClient.php Integration with Payment-Service

**Status**: Planning
**File**: `/home/bitrix/www/local/classes/Integration/Kaspi/ApiClient.php`
**Date**: 2025-11-03

---

## Current State (Hardcoded БINs)

```php
// Before Phase 3:
public function createRemotePay($params)
{
    $params['DeviceToken'] = Option::get('onelab.kaspipay', "device_token", '');
    $params['OrganizationBin'] = '891027350515';  // ❌ HARDCODED

    return $this->sendRequest(
        '/r3/v01/remote/create/',
        'POST',
        $params
    );
}
```

**Problems**:
- All orders use same БIN (891027350515) regardless of seller
- No multi-tenant payment routing
- Can't differentiate which seller money goes to

---

## Target State (Dynamic БIN Lookup)

```php
// After Phase 3:
public function createRemotePay($params)
{
    // Get shop_id from context (order, product, etc.)
    $shopId = $this->getShopIdFromContext();

    // Call payment-service to get correct БIN for this shop_id
    $paymentConfig = $this->getPaymentConfig($shopId);

    $params['DeviceToken'] = $paymentConfig['device_token'];
    $params['OrganizationBin'] = $paymentConfig['organization_bin'];

    return $this->sendRequest(
        '/r3/v01/remote/create/',
        'POST',
        $params
    );
}
```

**Benefits**:
- ✅ Money goes to correct seller's account
- ✅ Multi-tenant payment routing works
- ✅ No hardcoding needed
- ✅ Centralized config on Railway

---

## Architecture

### Payment Flow (Phase 3)

```
Order (shop_id=121038 for Eileen)
    ↓
ApiClient.createRemotePay()
    ↓
Call payment-service: GET /api/payment/config?shop_id=121038
    ↓
payment-service returns:
{
    "shop_id": 121038,
    "organization_bin": "920317450731",
    "device_token": "xxxxx",
    "is_active": true
}
    ↓
Use returned БIN + DeviceToken for Kaspi API call
    ↓
Kaspi creates payment → Money to Eileen's account ✅
```

### Code Changes Required

#### 1. Add Payment-Service Client Class

**New file**: `/local/classes/Integration/PaymentService/Client.php`

```php
<?php

namespace Integration\PaymentService;

class Client
{
    protected $apiUrl = 'https://payment-service.up.railway.app/api';
    protected $apiKey = null;  // Optional for Railway

    public function __construct($apiUrl = null, $apiKey = null)
    {
        if ($apiUrl) $this->apiUrl = $apiUrl;
        if ($apiKey) $this->apiKey = $apiKey;
    }

    /**
     * Get payment configuration for a shop
     *
     * @param int $shopId - Seller's shop_id (e.g., 121038 for Eileen)
     * @return array - {shop_id, organization_bin, device_token, is_active}
     */
    public function getPaymentConfig($shopId)
    {
        $response = $this->sendRequest(
            '/payment/config',
            'GET',
            [],
            ['shop_id' => $shopId]
        );

        if ($response['http_code'] == 200) {
            return json_decode($response['body'], true);
        }

        throw new \Exception("Failed to get payment config: " . $response['http_code']);
    }

    /**
     * Create payment log in payment-service
     */
    public function createPaymentLog($logData)
    {
        return $this->sendRequest(
            '/payment/log',
            'POST',
            $logData
        );
    }

    /**
     * Send HTTP request to payment-service
     */
    protected function sendRequest($path, $method = 'GET', $data = [], $queryParams = [])
    {
        $url = $this->apiUrl . $path;

        $curl = curl_init();

        if ($method === 'POST' || $method === 'PUT') {
            curl_setopt($curl, CURLOPT_CUSTOMREQUEST, $method);
            curl_setopt($curl, CURLOPT_POSTFIELDS, json_encode($data));
        } elseif ($queryParams) {
            $url .= '?' . http_build_query($queryParams);
        }

        curl_setopt($curl, CURLOPT_URL, $url);
        curl_setopt($curl, CURLOPT_HTTPHEADER, ['Content-Type: application/json']);
        curl_setopt($curl, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($curl, CURLOPT_TIMEOUT, 10);
        curl_setopt($curl, CURLOPT_SSL_VERIFYPEER, false);

        $response = curl_exec($curl);
        $httpCode = curl_getinfo($curl, CURLINFO_HTTP_CODE);
        curl_close($curl);

        return [
            'http_code' => $httpCode,
            'body' => $response
        ];
    }
}
```

#### 2. Update ApiClient.php

**Changes to existing methods**:

```php
<?php

namespace Integration\Kaspi;

use Integration\PaymentService\Client as PaymentServiceClient;
use Bitrix\Main\Config\Option;

class ApiClient
{
    protected $apiUrl = 'https://qrapi-cert-ip.kaspi.kz';
    protected $paymentServiceClient;
    protected $defaultShopId = 121038;  // Fallback

    public function __construct($params = [])
    {
        $this->paymentServiceClient = new PaymentServiceClient(
            $params['payment_service_url'] ?? 'https://payment-service.up.railway.app/api',
            $params['payment_service_key'] ?? null
        );
    }

    /**
     * Get payment config from payment-service
     * With fallback to hardcoded values for backwards compatibility
     */
    protected function getPaymentConfig($shopId = null)
    {
        if (!$shopId) {
            $shopId = $this->getShopIdFromContext();
        }

        try {
            return $this->paymentServiceClient->getPaymentConfig($shopId);
        } catch (\Exception $e) {
            // Fallback for testing/development
            \Bitrix\Main\Diag\Debug::writeToFile(
                'getPaymentConfig failed for shop_id=' . $shopId . ': ' . $e->getMessage(),
                'payment_service_error.log'
            );

            // Return default config
            return [
                'shop_id' => $shopId,
                'organization_bin' => '891027350515',  // Default fallback
                'device_token' => Option::get('onelab.kaspipay', 'device_token', ''),
                'is_active' => true
            ];
        }
    }

    /**
     * Extract shop_id from current context
     *
     * Priority:
     * 1. Function parameter (if passed)
     * 2. Order object if in order processing
     * 3. Product's shop_id if processing products
     * 4. User's shop_id from JWT token
     * 5. Default shop_id
     */
    protected function getShopIdFromContext()
    {
        global $GLOBALS;

        // Check if we have order context
        if (!empty($GLOBALS['arOrder']['SHOP_ID'])) {
            return (int)$GLOBALS['arOrder']['SHOP_ID'];
        }

        // Check if we have product context
        if (!empty($GLOBALS['arProduct']['SHOP_ID'])) {
            return (int)$GLOBALS['arProduct']['SHOP_ID'];
        }

        // Check request parameters
        if (!empty($_REQUEST['shop_id'])) {
            return (int)$_REQUEST['shop_id'];
        }

        // Check from HTTP header (if using API)
        if (!empty($_SERVER['HTTP_X_SHOP_ID'])) {
            return (int)$_SERVER['HTTP_X_SHOP_ID'];
        }

        // Default fallback
        return $this->defaultShopId;
    }

    /**
     * Updated: createRemotePay with dynamic БIN
     */
    public function createRemotePay($params, $shopId = null)
    {
        // Get payment config from payment-service
        $config = $this->getPaymentConfig($shopId);

        $params['DeviceToken'] = $config['device_token'];
        $params['OrganizationBin'] = $config['organization_bin'];

        // Log payment attempt
        try {
            $this->paymentServiceClient->createPaymentLog([
                'shop_id' => $config['shop_id'],
                'organization_bin' => $config['organization_bin'],
                'operation_type' => 'create',
                'amount' => $params['Amount'] ?? null,
                'status' => 'Wait'
            ]);
        } catch (\Exception $e) {
            // Log error but don't block payment
            \Bitrix\Main\Diag\Debug::writeToFile(
                'createPaymentLog failed: ' . $e->getMessage(),
                'payment_service_error.log'
            );
        }

        return $this->sendRequest(
            '/r3/v01/remote/create/',
            'POST',
            $params
        );
    }

    /**
     * Updated: getCreteQr with dynamic БIN
     */
    public function getCreteQr($params, $shopId = null)
    {
        $config = $this->getPaymentConfig($shopId);

        $params['DeviceToken'] = $config['device_token'];
        $params['OrganizationBin'] = $config['organization_bin'];

        return $this->sendRequest(
            '/r3/v01/qr/create',
            'POST',
            $params
        );
    }

    /**
     * Updated: createLink with dynamic БIN
     */
    public function createLink($params, $shopId = null)
    {
        $config = $this->getPaymentConfig($shopId);

        $params['DeviceToken'] = $config['device_token'];
        $params['OrganizationBin'] = $config['organization_bin'];

        return $this->sendRequest(
            '/r3/v01/qr/create-link',
            'POST',
            $params
        );
    }

    /**
     * Keep all existing sendRequest methods unchanged
     */
    // ... rest of existing code ...
}
```

---

## Implementation Steps

### Step 1: Create PaymentService Client Class
- Create `/local/classes/Integration/PaymentService/Client.php`
- Implement HTTP client for payment-service API
- Add error handling and fallback logic

### Step 2: Update ApiClient.php
- Add `getPaymentConfig()` method
- Add `getShopIdFromContext()` method
- Update all public payment methods to use dynamic БINs
- Maintain backwards compatibility with fallback values

### Step 3: Test Integration
- Test with each seller (shop_id: 121038, 576631, 75509, etc.)
- Verify money goes to correct accounts
- Monitor error logs

### Step 4: Deploy to Production
- Commit updated ApiClient.php
- SCP to production server `/home/bitrix/www/local/classes/Integration/`
- Verify payment-service is deployed on Railway
- Monitor Kaspi API responses

---

## Shop ID Context Hierarchy

```
┌──────────────────────────────────────────┐
│ Where does shop_id come from?            │
└──────────────────────────────────────────┘
           ↓
   ┌───────────────────┐
   │ Order object?     │ → Use order.shop_id
   │ (when creating    │
   │  payment)         │
   └───────────────────┘
           ↓
   ┌───────────────────┐
   │ Product context?  │ → Use product.shop_id
   │ (product's        │
   │  seller)          │
   └───────────────────┘
           ↓
   ┌───────────────────┐
   │ Request params?   │ → Use ?shop_id=121038
   │ (?shop_id=...)    │
   └───────────────────┘
           ↓
   ┌───────────────────┐
   │ HTTP header?      │ → Use X-Shop-Id header
   │ (X-Shop-Id)       │
   └───────────────────┘
           ↓
   ┌───────────────────┐
   │ Default fallback  │ → Use 121038 (Eileen)
   └───────────────────┘
```

---

## Rollback Plan

If payment-service is down or unavailable:

1. ApiClient catches exception from payment-service
2. Falls back to hardcoded БINs (existing behavior)
3. Logs error for debugging
4. Returns fallback config to resume payments
5. Monitor error logs and fix payment-service

---

## Performance Considerations

### Current Flow (Direct Kaspi)
```
Order → ApiClient → Kaspi API → Response
         (direct call)
```

### With Payment-Service (Phase 3)
```
Order → ApiClient → Payment-Service (HTTP call) → Kaspi API → Response
         (adds ~50-100ms)
```

**Optimization**: Add caching in ApiClient
```php
protected $configCache = [];

public function getPaymentConfig($shopId)
{
    // Check cache first
    if (isset($this->configCache[$shopId])) {
        return $this->configCache[$shopId];
    }

    // Call payment-service
    $config = $this->paymentServiceClient->getPaymentConfig($shopId);

    // Cache for 1 hour
    $this->configCache[$shopId] = $config;

    return $config;
}
```

---

## Next Steps (After Phase 3)

- **Phase 4**: Add payment status polling via cron job
- **Phase 5**: Setup CRM webhooks for payment notifications
- **Phase 6**: Test all 7 sellers end-to-end

---

Last Updated: 2025-11-03
