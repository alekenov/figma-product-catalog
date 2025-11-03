<?php
/**
 * Payment Service Client
 *
 * HTTP client for communicating with Railway payment-service
 * Handles БIN lookup, device token retrieval, and payment logging
 *
 * Usage:
 *   $client = new PaymentServiceClient('https://payment-service.up.railway.app/api');
 *   $config = $client->getPaymentConfig(121038);  // Get config for shop_id 121038
 *   echo $config['organization_bin'];  // 920317450731
 */

namespace Integration\PaymentService;

class Client
{
    protected $apiUrl = 'https://payment-service.up.railway.app/api';
    protected $apiKey = null;
    protected $timeout = 10;

    /**
     * Constructor
     *
     * @param string $apiUrl - Base URL of payment-service API
     * @param string|null $apiKey - Optional API key for authentication
     */
    public function __construct($apiUrl = null, $apiKey = null)
    {
        if ($apiUrl) {
            $this->apiUrl = rtrim($apiUrl, '/');
        }
        if ($apiKey) {
            $this->apiKey = $apiKey;
        }
    }

    /**
     * Get payment configuration for a shop
     *
     * @param int $shopId - Seller's element ID from Bitrix (e.g., 121038 for Eileen)
     * @return array - Payment config with keys:
     *   - shop_id: int (e.g., 121038)
     *   - organization_bin: string (e.g., "920317450731")
     *   - device_token: string (e.g., "7ae52134-ea55-4f3b-bc6a-b65c40eda3ad")
     *   - is_active: bool (true/false)
     *   - provider: string (e.g., "kaspi")
     *
     * @throws \Exception if shop_id not found or API error
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
            $data = json_decode($response['body'], true);

            if (!$data) {
                throw new \Exception("Invalid JSON response from payment-service");
            }

            // Validate required fields
            $required = ['shop_id', 'organization_bin', 'is_active'];
            foreach ($required as $field) {
                if (!isset($data[$field])) {
                    throw new \Exception("Missing required field: {$field}");
                }
            }

            return $data;
        }

        if ($response['http_code'] == 404) {
            throw new \Exception("Shop ID {$shopId} not found in payment config");
        }

        throw new \Exception(
            "Payment-service error ({$response['http_code']}): {$response['body']}"
        );
    }

    /**
     * Create payment log entry in payment-service
     *
     * Logs all payment operations for auditing and debugging
     *
     * @param array $logData - Payment log data:
     *   - shop_id: int (required)
     *   - organization_bin: string (required)
     *   - operation_type: string ('create', 'status', 'refund')
     *   - external_id: string|null (Kaspi QrPaymentId)
     *   - amount: int|null (in kopecks)
     *   - status: string ('Wait', 'Processed', 'Error')
     *   - error_message: string|null
     *
     * @return array - Log entry response
     */
    public function createPaymentLog($logData)
    {
        // Validate required fields
        $required = ['shop_id', 'organization_bin', 'operation_type'];
        foreach ($required as $field) {
            if (!isset($logData[$field])) {
                throw new \Exception("Missing required field for log: {$field}");
            }
        }

        $response = $this->sendRequest(
            '/payment/log',
            'POST',
            $logData
        );

        if ($response['http_code'] >= 200 && $response['http_code'] < 300) {
            return json_decode($response['body'], true);
        }

        // Log error but don't throw - logging shouldn't block payments
        \Bitrix\Main\Diag\Debug::writeToFile(
            'Payment log creation failed (' . $response['http_code'] . '): ' . $response['body'],
            'kaspi_payment_service.log'
        );

        return null;
    }

    /**
     * Update payment status in payment-service
     *
     * @param int $shopId
     * @param string $externalId - Kaspi QrPaymentId
     * @param string $status - 'Processed', 'Error', etc.
     * @param string|null $errorMessage
     *
     * @return array - Updated log entry
     */
    public function updatePaymentStatus($shopId, $externalId, $status, $errorMessage = null)
    {
        $logData = [
            'shop_id' => $shopId,
            'external_id' => $externalId,
            'status' => $status,
            'operation_type' => 'status'
        ];

        if ($errorMessage) {
            $logData['error_message'] = $errorMessage;
        }

        return $this->createPaymentLog($logData);
    }

    /**
     * Check if payment-service is healthy
     *
     * @return bool - true if service is accessible
     */
    public function healthCheck()
    {
        try {
            $response = $this->sendRequest('/health', 'GET');
            return $response['http_code'] == 200;
        } catch (\Exception $e) {
            return false;
        }
    }

    /**
     * Send HTTP request to payment-service
     *
     * @param string $path - API endpoint (e.g., '/payment/config')
     * @param string $method - HTTP method (GET, POST, PUT, DELETE)
     * @param array $data - Request body (for POST/PUT)
     * @param array $queryParams - Query parameters
     *
     * @return array - Response with keys:
     *   - http_code: int
     *   - body: string (raw response body)
     *   - error: string|null (curl error if any)
     *
     * @throws \Exception on curl error
     */
    protected function sendRequest($path, $method = 'GET', $data = [], $queryParams = [])
    {
        $url = $this->apiUrl . $path;

        $curl = curl_init();

        // Build URL with query parameters
        if (!empty($queryParams)) {
            $url .= '?' . http_build_query($queryParams);
        }

        // Set HTTP method and data
        if ($method === 'POST' || $method === 'PUT') {
            curl_setopt($curl, CURLOPT_CUSTOMREQUEST, $method);
            curl_setopt($curl, CURLOPT_POSTFIELDS, json_encode($data));
        } elseif ($method === 'DELETE') {
            curl_setopt($curl, CURLOPT_CUSTOMREQUEST, 'DELETE');
        }

        // Set common options
        curl_setopt($curl, CURLOPT_URL, $url);
        curl_setopt($curl, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($curl, CURLOPT_TIMEOUT, $this->timeout);
        curl_setopt($curl, CURLOPT_CONNECTTIMEOUT, 5);

        // Headers
        $headers = [
            'Content-Type: application/json',
            'User-Agent: Bitrix ApiClient/1.0'
        ];

        if ($this->apiKey) {
            $headers[] = 'Authorization: Bearer ' . $this->apiKey;
        }

        curl_setopt($curl, CURLOPT_HTTPHEADER, $headers);

        // SSL options (disable for development, enable for production)
        // curl_setopt($curl, CURLOPT_SSL_VERIFYPEER, true);
        // curl_setopt($curl, CURLOPT_SSL_VERIFYHOST, 2);
        curl_setopt($curl, CURLOPT_SSL_VERIFYPEER, false);  // TODO: Enable in production
        curl_setopt($curl, CURLOPT_SSL_VERIFYHOST, false);

        // Execute request
        $body = curl_exec($curl);
        $httpCode = curl_getinfo($curl, CURLINFO_HTTP_CODE);
        $curlError = curl_error($curl);

        curl_close($curl);

        // Log curl errors
        if ($curlError) {
            \Bitrix\Main\Diag\Debug::writeToFile(
                'Curl error: ' . $curlError . ' (URL: ' . $url . ')',
                'kaspi_payment_service.log'
            );
        }

        return [
            'http_code' => (int)$httpCode,
            'body' => $body,
            'error' => $curlError ?: null
        ];
    }
}
