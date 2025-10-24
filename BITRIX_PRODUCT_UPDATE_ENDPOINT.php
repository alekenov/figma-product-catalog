<?php
/**
 * Bitrix API v2 Endpoint for Product Updates from Railway
 *
 * File location: /home/bitrix/www/api/v2/products/update-from-railway/index.php
 *
 * This endpoint receives product updates from Railway backend and applies them
 * to the Bitrix CMS. It handles price, name, description, image, and enabled status.
 *
 * Security: Requires valid Authorization: Bearer token
 *
 * Usage:
 * PUT /api/v2/products/update-from-railway
 * Authorization: Bearer {token}
 *
 * {
 *     "id": 668826,
 *     "title": "Эустомы в пачках ФИОЛЕТОВЫЕ",
 *     "price": "4 950 ₸",
 *     "image": "https://example.com/image.jpg",
 *     "isAvailable": true,
 *     "description": "Beautiful purple eustomas"
 * }
 */

// Configuration
define('NO_KEEP_STATISTIC', true);
define('NOT_CHECK_PERMISSIONS', true);
define('STOP_STATISTICS', true);
define('DisableEventsCheck', true);

require($_SERVER['DOCUMENT_ROOT'] . '/bitrix/modules/main/include/prolog_before.php');

use Bitrix\Main\Loader;
use Bitrix\Main\Web\Json;
use Bitrix\Main\Context;

header('Content-Type: application/json; charset=utf-8');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: PUT, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type, Authorization');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit;
}

if ($_SERVER['REQUEST_METHOD'] !== 'PUT') {
    http_response_code(405);
    echo Json::encode(['status' => false, 'error' => 'Only PUT method allowed'], JSON_UNESCAPED_UNICODE);
    exit;
}

// Authentication: Check Bearer token
$request = Context::getCurrent()->getRequest();
$headers = $request->getHeaders();

$token = (string)$request->get('access_token');
if (!$token) {
    $authHeader = (string)$headers->get('Authorization');
    if ($authHeader && stripos($authHeader, 'Bearer ') === 0) {
        $token = trim(substr($authHeader, 7));
    }
}

// Validate token (from environment or hardcoded)
$validToken = getenv('RAILWAY_API_TOKEN') ?: 'ABE7142D-D8AB-76AF-8D6C-2C4FAEA9B144';
if ($token !== $validToken) {
    http_response_code(401);
    echo Json::encode(['status' => false, 'error' => 'Invalid API token'], JSON_UNESCAPED_UNICODE);
    exit;
}

// Parse request body
$rawBody = file_get_contents('php://input');
$payload = json_decode($rawBody, true);

if (!is_array($payload)) {
    http_response_code(400);
    echo Json::encode(['status' => false, 'error' => 'Invalid JSON payload'], JSON_UNESCAPED_UNICODE);
    exit;
}

// Validate required fields
$productId = (int)($payload['id'] ?? 0);
if ($productId <= 0) {
    http_response_code(400);
    echo Json::encode(['status' => false, 'error' => 'Missing or invalid product id'], JSON_UNESCAPED_UNICODE);
    exit;
}

try {
    // Load required modules
    if (!Loader::includeModule('iblock')) {
        http_response_code(500);
        echo Json::encode(['status' => false, 'error' => 'IBlock module unavailable'], JSON_UNESCAPED_UNICODE);
        exit;
    }

    // Get current product
    $res = CIBlockElement::GetByID($productId);
    if (!($element = $res->GetNextElement())) {
        http_response_code(404);
        echo Json::encode(['status' => false, 'error' => 'Product not found'], JSON_UNESCAPED_UNICODE);
        exit;
    }

    $elementFields = $element->GetFields();
    $elementProps = $element->GetProperties();

    // Prepare update fields
    $updateFields = [
        'MODIFIED_BY' => 1,  // System user
        'DATE_MODIFY' => new \Bitrix\Main\Type\DateTime()
    ];

    // Update name
    if (!empty($payload['title'])) {
        $updateFields['NAME'] = (string)$payload['title'];
    }

    // Update enabled status
    if (isset($payload['isAvailable'])) {
        $updateFields['ACTIVE'] = $payload['isAvailable'] ? 'Y' : 'N';
    }

    // Update image (preview picture)
    if (!empty($payload['image'])) {
        $imageUrl = (string)$payload['image'];

        // Download image from URL and add to Bitrix
        $fileTmp = download_file($imageUrl);
        if ($fileTmp) {
            $fileArray = CFile::MakeFileArray($fileTmp);
            if ($fileArray) {
                $updateFields['PREVIEW_PICTURE'] = $fileArray;
                @unlink($fileTmp);  // Clean up temp file
            }
        }
    }

    // Update properties
    $updateProps = [];

    // Update price
    if (isset($payload['price'])) {
        $price = (string)$payload['price'];
        // Property code might be 'PRICE', 'CML2_ARTICLE', etc - depends on your Bitrix setup
        // Look for price property in your IBlock
        $updateProps['PRICE'] = $price;
    }

    // Update description
    if (!empty($payload['description'])) {
        $updateFields['DETAIL_TEXT'] = (string)$payload['description'];
    }

    // Update element
    $element = new CIBlockElement;

    if (!$element->Update($productId, $updateFields)) {
        http_response_code(500);
        echo Json::encode([
            'status' => false,
            'error' => 'Failed to update product: ' . $element->LAST_ERROR
        ], JSON_UNESCAPED_UNICODE);
        exit;
    }

    // Update properties if any
    if (!empty($updateProps)) {
        $el = new CIBlockElement;
        $el->SetPropertyValues($productId, false, $updateProps);
    }

    // Success response
    http_response_code(200);
    echo Json::encode([
        'status' => true,
        'product_id' => $productId,
        'message' => "Product {$productId} updated successfully",
        'updated_fields' => array_keys($updateFields)
    ], JSON_UNESCAPED_UNICODE);

} catch (\Throwable $e) {
    error_log("Railway Product Update Error: " . $e->getMessage());
    http_response_code(500);
    echo Json::encode([
        'status' => false,
        'error' => 'Internal error: ' . $e->getMessage()
    ], JSON_UNESCAPED_UNICODE);
}


/**
 * Helper: Download file from URL
 *
 * @param string $url
 * @return string|false - Temp file path or false
 */
function download_file($url)
{
    $timeout = 30;

    // Try curl first
    if (function_exists('curl_init')) {
        $ch = curl_init();
        curl_setopt($ch, CURLOPT_URL, $url);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_TIMEOUT, $timeout);
        curl_setopt($ch, CURLOPT_FOLLOWLOCATION, true);
        curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);

        $data = curl_exec($ch);
        curl_close($ch);

        if ($data !== false) {
            $tmpFile = tempnam(sys_get_temp_dir(), 'bitrix_download_');
            if (file_put_contents($tmpFile, $data)) {
                return $tmpFile;
            }
        }
    }

    // Fallback to fopen
    if (ini_get('allow_url_fopen')) {
        $data = file_get_contents($url, false, stream_context_create([
            'http' => ['timeout' => $timeout],
            'https' => ['timeout' => $timeout]
        ]));

        if ($data !== false) {
            $tmpFile = tempnam(sys_get_temp_dir(), 'bitrix_download_');
            if (file_put_contents($tmpFile, $data)) {
                return $tmpFile;
            }
        }
    }

    return false;
}
