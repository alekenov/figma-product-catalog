<?php
/**
 * Updated Kaspi API Client with Payment-Service Integration
 *
 * Phase 3 Integration: Multi-БIN routing for multiple sellers
 *
 * Changes from original:
 * 1. Added PaymentServiceClient integration
 * 2. Added getPaymentConfig() method for dynamic БIN lookup
 * 3. Added getShopIdFromContext() method for extracting shop_id
 * 4. Updated all payment methods to use dynamic БINs
 * 5. Added payment logging to payment-service
 *
 * Key Methods Changed:
 * - createRemotePay($params, $shopId = null)
 * - getCreteQr($params, $shopId = null)
 * - createLink($params, $shopId = null)
 * - createLinkTest($params, $shopId = null)
 * - createRemotePayTest($params, $shopId = null)
 * - paymentReturn($params, $shopId = null)
 */

namespace Integration\Kaspi;

use Integration\PaymentService\Client as PaymentServiceClient;
use Bitrix\Main\Config\Option;

class ApiClient
{
    protected $apiUrl = 'https://qrapi-cert-ip.kaspi.kz';
    protected $paymentServiceClient;
    protected $defaultShopId = 121038;  // Fallback: Eileen flowers
    protected $configCache = [];  // Cache payment configs

    /**
     * Constructor
     *
     * Initializes Kaspi API client and payment-service client
     */
    public function __construct($params = [])
    {
        // Initialize payment-service client
        $paymentServiceUrl = $params['payment_service_url']
            ?? Option::get('onelab.kaspipay', 'payment_service_url', '')
            ?? 'https://payment-service.up.railway.app/api';

        $this->paymentServiceClient = new PaymentServiceClient(
            $paymentServiceUrl,
            $params['payment_service_key'] ?? null
        );
    }

    /**
     * Get payment configuration from payment-service
     *
     * Implements fallback to hardcoded values for backwards compatibility
     *
     * @param int|null $shopId - If null, extracts from context
     * @return array - Config with shop_id, organization_bin, device_token, is_active
     */
    protected function getPaymentConfig($shopId = null)
    {
        if (!$shopId) {
            $shopId = $this->getShopIdFromContext();
        }

        // Check cache first (1-hour cache)
        if (isset($this->configCache[$shopId])) {
            $cacheEntry = $this->configCache[$shopId];
            if (time() - $cacheEntry['cached_at'] < 3600) {
                return $cacheEntry['data'];
            }
        }

        try {
            // Call payment-service to get config
            $config = $this->paymentServiceClient->getPaymentConfig($shopId);

            // Cache the result
            $this->configCache[$shopId] = [
                'data' => $config,
                'cached_at' => time()
            ];

            return $config;

        } catch (\Exception $e) {
            // Log error
            \Bitrix\Main\Diag\Debug::writeToFile(
                'Payment config lookup failed for shop_id=' . $shopId . ': ' . $e->getMessage(),
                'kaspi_payment_service.log'
            );

            // Return fallback config (hardcoded for backwards compatibility)
            return [
                'shop_id' => $shopId,
                'organization_bin' => '891027350515',  // Default Cvety.kz БИН
                'device_token' => Option::get('onelab.kaspipay', 'device_token', ''),
                'is_active' => true,
                'provider' => 'kaspi',
                'fallback' => true  // Mark as fallback
            ];
        }
    }

    /**
     * Extract shop_id from current context
     *
     * Priority:
     * 1. Global $arOrder or $arProduct
     * 2. Request parameters
     * 3. HTTP headers
     * 4. Default value
     *
     * @return int - Shop ID (e.g., 121038 for Eileen)
     */
    protected function getShopIdFromContext()
    {
        // Check global order context
        if (!empty($GLOBALS['arOrder']) && !empty($GLOBALS['arOrder']['SHOP_ID'])) {
            return (int)$GLOBALS['arOrder']['SHOP_ID'];
        }

        // Check global product context
        if (!empty($GLOBALS['arProduct']) && !empty($GLOBALS['arProduct']['SHOP_ID'])) {
            return (int)$GLOBALS['arProduct']['SHOP_ID'];
        }

        // Check request parameters
        if (!empty($_REQUEST['shop_id'])) {
            return (int)$_REQUEST['shop_id'];
        }

        // Check HTTP header (for API calls)
        if (!empty($_SERVER['HTTP_X_SHOP_ID'])) {
            return (int)$_SERVER['HTTP_X_SHOP_ID'];
        }

        // Default fallback
        return $this->defaultShopId;
    }

    /**
     * Create remote payment (QR code payment)
     *
     * UPDATED: Uses dynamic БIN from payment-service
     *
     * @param array $params - Payment parameters (Amount, Currency, etc.)
     * @param int|null $shopId - Optional shop_id override
     * @return array - Kaspi API response
     */
    public function createRemotePay($params, $shopId = null)
    {
        // Get payment config with dynamic БIN
        $config = $this->getPaymentConfig($shopId);

        // Set БIN and device token from config
        $params['DeviceToken'] = $config['device_token'];
        $params['OrganizationBin'] = $config['organization_bin'];

        // Log payment attempt to payment-service
        try {
            $this->paymentServiceClient->createPaymentLog([
                'shop_id' => $config['shop_id'],
                'organization_bin' => $config['organization_bin'],
                'operation_type' => 'create',
                'amount' => $params['Amount'] ?? null,
                'status' => 'Wait',
                'provider' => 'kaspi'
            ]);
        } catch (\Exception $e) {
            \Bitrix\Main\Diag\Debug::writeToFile(
                'Failed to log payment creation: ' . $e->getMessage(),
                'kaspi_payment_service.log'
            );
        }

        return $this->sendRequest(
            '/r3/v01/remote/create/',
            'POST',
            $params
        );
    }

    /**
     * Get status of existing payment
     *
     * @param string $id - QrPaymentId from Kaspi
     * @return array - Payment status from Kaspi
     */
    public function status($id)
    {
        return $this->sendRequest(
            '/r3/v01/payment/status/' . $id . '/'
        );
    }

    /**
     * Create QR code
     *
     * UPDATED: Uses dynamic БIN from payment-service
     *
     * @param array $params - QR parameters
     * @param int|null $shopId - Optional shop_id override
     * @return array - Kaspi response
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
     * Create payment link
     *
     * UPDATED: Uses dynamic БIN from payment-service
     *
     * @param array $params - Link parameters
     * @param int|null $shopId - Optional shop_id override
     * @return array - Kaspi response
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
     * Create payment link (test version)
     *
     * UPDATED: Uses dynamic БIN from payment-service
     *
     * @param array $params
     * @param int|null $shopId
     * @return array
     */
    public function createLinkTest($params, $shopId = null)
    {
        $config = $this->getPaymentConfig($shopId);

        $params['DeviceToken'] = $config['device_token'];
        $params['OrganizationBin'] = $config['organization_bin'];

        return $this->sendRequestTest(
            '/r3/v01/qr/create-link',
            'POST',
            $params
        );
    }

    /**
     * Create remote payment (test version)
     *
     * UPDATED: Uses dynamic БIN from payment-service
     *
     * @param array $params
     * @param int|null $shopId
     * @return array
     */
    public function createRemotePayTest($params, $shopId = null)
    {
        $config = $this->getPaymentConfig($shopId);

        $params['DeviceToken'] = $config['device_token'];
        $params['OrganizationBin'] = $config['organization_bin'];

        return $this->sendRequestTest(
            '/r3/v01/remote/create/',
            'POST',
            $params
        );
    }

    /**
     * Payment return/refund
     *
     * UPDATED: Uses dynamic БIN from payment-service
     *
     * @param array $params
     * @param int|null $shopId
     * @return array
     */
    public function paymentReturn($params, $shopId = null)
    {
        $config = $this->getPaymentConfig($shopId);

        $params['DeviceToken'] = $config['device_token'];
        $params['OrganizationBin'] = $config['organization_bin'];

        return $this->sendRequestTest(
            '/r3/v01/remote/create/',
            'POST',
            $params
        );
    }

    /**
     * Get remote client info
     *
     * UPDATED: Uses dynamic БIN from payment-service
     *
     * @param array $params
     * @param int|null $shopId
     * @return array
     */
    public function remoteClientInfo($params, $shopId = null)
    {
        $config = $this->getPaymentConfig($shopId);

        $params['DeviceToken'] = $config['device_token'];

        return $this->sendRequestTest(
            '/r3/v01/remote/client-info',
            'GET',
            $params
        );
    }

    /**
     * Get payment details
     *
     * @param array $params
     * @return array
     */
    public function get($params)
    {
        return $this->sendRequest(
            '/r3/v01/payment/details?QrPaymentId=5304664357&DeviceToken=f9abfcd9-df01-427c-8af5-5409cc2c1b37',
            'GET'
        );
    }

    /**
     * Send request to Kaspi API (production)
     *
     * NOTE: All sendRequest methods remain unchanged from original
     *
     * @param string $path
     * @param string $method
     * @param mixed $data
     * @param mixed $queryParams
     * @param array $headers
     * @return array
     */
    protected function sendRequest($path, $method = 'GET', $data = [], $queryParams = [], $headers = [])
    {
        $url = $this->apiUrl . $path;
        $curl = curl_init();

        $orange = false;

        if (isset($data['orange'])) {
            $orange = true;
            unset($data['orange']);
        }

        switch ($method) {
            case 'POST':
                curl_setopt($curl, CURLOPT_POST, true);
                if ($data) {
                    curl_setopt($curl, CURLOPT_POSTFIELDS, json_encode($data));
                }
                break;
            case 'PUT':
                curl_setopt($curl, CURLOPT_CUSTOMREQUEST, 'PUT');
                if ($data) {
                    curl_setopt($curl, CURLOPT_POSTFIELDS, http_build_query($data));
                }
                break;
            case 'DELETE':
                curl_setopt($curl, CURLOPT_CUSTOMREQUEST, 'DELETE');
                if ($data) {
                    curl_setopt($curl, CURLOPT_POSTFIELDS, http_build_query($data));
                }
                break;
            default:
                if ($data || $queryParams) {
                    $url .= '?' . http_build_query(array_merge($data, $queryParams));
                }
        }

        if ($queryParams && in_array($method, ['POST', 'PUT', 'DELETE'])) {
            $url .= '?' . http_build_query($queryParams);
        }

        curl_setopt($curl, CURLOPT_URL, $url);
        curl_setopt($curl, CURLOPT_HTTPHEADER, array_merge(['Content-Type:application/json'], $headers));
        curl_setopt($curl, CURLOPT_RETURNTRANSFER, true);

        if ($orange) {
            curl_setopt($curl, CURLOPT_SSLCERT, '/home/bitrix/kaspi_certificates/orange/certificate.cer');
            curl_setopt($curl, CURLOPT_SSLKEY, '/home/bitrix/kaspi_certificates/orange/private_rsa.key');
            curl_setopt($curl, CURLOPT_SSLKEYPASSWD, 'kGGbu?;t*u_3W#');
        } else {
            curl_setopt($curl, CURLOPT_SSLCERT, '/home/bitrix/kaspi_certificates/prod/cvety.cer');
            curl_setopt($curl, CURLOPT_SSLKEY, '/home/bitrix/kaspi_certificates/prod/cvety-new.key');
            curl_setopt($curl, CURLOPT_SSLKEYPASSWD, 'sy3t6G2HhuG1m4pEK8AJ2');
        }

        $response = curl_exec($curl);
        $header_size = curl_getinfo($curl, CURLINFO_HEADER_SIZE);
        $headerCode = curl_getinfo($curl, CURLINFO_HTTP_CODE);
        $responseBody = substr($response, $header_size);
        $responseHeaders = substr($response, 0, $header_size);
        $ip = curl_getinfo($curl, CURLINFO_PRIMARY_IP);
        $curlErrors = curl_error($curl);
        $sentHeaders = curl_getinfo($curl, CURLINFO_HEADER_OUT);

        curl_close($curl);

        return [
            'data' => json_decode($responseHeaders, true),
            'http_code' => trim($headerCode),
            'headers' => trim($responseHeaders),
            'sentHeaders' => trim($sentHeaders),
            'sentData' => $data,
            'ip' => trim($ip),
            'curlErrors' => $curlErrors,
            'method' => $method . ':' . $url,
            'timestamp' => date('Y-m-d h:i:sP'),
        ];
    }

    /**
     * Send test request to Kaspi API (test mode)
     *
     * @param string $path
     * @param string $method
     * @param mixed $data
     * @param mixed $queryParams
     * @param array $headers
     * @return array
     */
    protected function sendRequestTest($path, $method = 'GET', $data = [], $queryParams = [], $headers = [])
    {
        $url = $this->apiUrl . $path;
        $curl = curl_init();

        switch ($method) {
            case 'POST':
                curl_setopt($curl, CURLOPT_POST, true);
                if ($data) {
                    curl_setopt($curl, CURLOPT_POSTFIELDS, json_encode($data));
                }
                break;
            case 'PUT':
                curl_setopt($curl, CURLOPT_CUSTOMREQUEST, 'PUT');
                if ($data) {
                    curl_setopt($curl, CURLOPT_POSTFIELDS, http_build_query($data));
                }
                break;
            case 'DELETE':
                curl_setopt($curl, CURLOPT_CUSTOMREQUEST, 'DELETE');
                if ($data) {
                    curl_setopt($curl, CURLOPT_POSTFIELDS, http_build_query($data));
                }
                break;
            default:
                if ($data || $queryParams) {
                    $url .= '?' . http_build_query(array_merge($data, $queryParams));
                }
        }

        if ($queryParams && in_array($method, ['POST', 'PUT', 'DELETE'])) {
            $url .= '?' . http_build_query($queryParams);
        }

        curl_setopt($curl, CURLOPT_URL, $url);
        curl_setopt($curl, CURLOPT_HTTPHEADER, array_merge(['Content-Type:application/json'], $headers));
        curl_setopt($curl, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($curl, CURLOPT_SSLCERT, '/home/bitrix/kaspi_certificates/prod/cvety.cer');
        curl_setopt($curl, CURLOPT_SSLKEY, '/home/bitrix/kaspi_certificates/prod/cvety-new.key');
        curl_setopt($curl, CURLOPT_SSLKEYPASSWD, '73V#-t]ogn');
        curl_setopt($curl, CURLOPT_CONNECTTIMEOUT, 10);

        $response = curl_exec($curl);
        $header_size = curl_getinfo($curl, CURLINFO_HEADER_SIZE);
        $headerCode = curl_getinfo($curl, CURLINFO_HTTP_CODE);
        $responseBody = substr($response, $header_size);
        $responseHeaders = substr($response, 0, $header_size);
        $ip = curl_getinfo($curl, CURLINFO_PRIMARY_IP);
        $curlErrors = curl_error($curl);
        $sentHeaders = curl_getinfo($curl, CURLINFO_HEADER_OUT);

        curl_close($curl);

        return [
            'data' => json_decode($responseHeaders, true),
            'http_code' => trim($headerCode),
            'headers' => trim($responseHeaders),
            'sentHeaders' => trim($sentHeaders),
            'sentData' => $data,
            'ip' => trim($ip),
            'curlErrors' => $curlErrors,
            'method' => $method . ':' . $url,
            'timestamp' => date('Y-m-d h:i:sP'),
        ];
    }
}
