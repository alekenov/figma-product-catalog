/**
 * Google Cloud Platform Authentication Service
 * Handles JWT signing and OAuth2 token generation for Vertex AI
 */

interface ServiceAccountKey {
  type: string;
  project_id: string;
  private_key_id: string;
  private_key: string;
  client_email: string;
  token_uri: string;
}

interface AccessTokenResponse {
  access_token: string;
  expires_in: number;
  token_type: string;
}

interface CachedToken {
  token: string;
  expiresAt: number;
}

// Simple in-memory token cache (resets on worker restart)
let tokenCache: CachedToken | null = null;

/**
 * Get a valid access token for Vertex AI API
 * Uses cached token if still valid, otherwise generates new one
 */
export async function getAccessToken(serviceAccountKeyJson: string): Promise<string> {
  // Check if we have a cached token that's still valid
  if (tokenCache && tokenCache.expiresAt > Date.now() + 60000) {
    return tokenCache.token;
  }

  // Parse service account key
  const serviceAccount: ServiceAccountKey = JSON.parse(serviceAccountKeyJson);

  // Create JWT assertion
  const jwt = await createJWT(serviceAccount);

  // Exchange JWT for access token
  const response = await fetch(serviceAccount.token_uri, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: new URLSearchParams({
      grant_type: 'urn:ietf:params:oauth:grant-type:jwt-bearer',
      assertion: jwt,
    }),
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Failed to get access token: ${response.status} ${error}`);
  }

  const data: AccessTokenResponse = await response.json();

  // Cache the token (expire 5 min before actual expiry for safety)
  tokenCache = {
    token: data.access_token,
    expiresAt: Date.now() + (data.expires_in - 300) * 1000,
  };

  return data.access_token;
}

/**
 * Create a signed JWT for Google OAuth2
 */
async function createJWT(serviceAccount: ServiceAccountKey): Promise<string> {
  const now = Math.floor(Date.now() / 1000);
  const expiry = now + 3600; // 1 hour

  // JWT Header
  const header = {
    alg: 'RS256',
    typ: 'JWT',
    kid: serviceAccount.private_key_id,
  };

  // JWT Claim Set
  const claimSet = {
    iss: serviceAccount.client_email,
    sub: serviceAccount.client_email,
    aud: serviceAccount.token_uri,
    iat: now,
    exp: expiry,
    scope: 'https://www.googleapis.com/auth/cloud-platform',
  };

  // Encode header and claim set
  const encodedHeader = base64UrlEncode(JSON.stringify(header));
  const encodedClaimSet = base64UrlEncode(JSON.stringify(claimSet));
  const message = `${encodedHeader}.${encodedClaimSet}`;

  // Sign with private key
  const signature = await signMessage(message, serviceAccount.private_key);
  const encodedSignature = base64UrlEncode(signature);

  return `${message}.${encodedSignature}`;
}

/**
 * Sign a message with RSA-SHA256 using Web Crypto API
 */
async function signMessage(message: string, privateKeyPem: string): Promise<ArrayBuffer> {
  // Extract private key from PEM format
  const pemContents = privateKeyPem
    .replace('-----BEGIN PRIVATE KEY-----', '')
    .replace('-----END PRIVATE KEY-----', '')
    .replace(/\s/g, '');

  // Decode base64
  const binaryKey = base64Decode(pemContents);

  // Import private key
  const cryptoKey = await crypto.subtle.importKey(
    'pkcs8',
    binaryKey,
    {
      name: 'RSASSA-PKCS1-v1_5',
      hash: 'SHA-256',
    },
    false,
    ['sign']
  );

  // Sign the message
  const encoder = new TextEncoder();
  const data = encoder.encode(message);
  const signature = await crypto.subtle.sign('RSASSA-PKCS1-v1_5', cryptoKey, data);

  return signature;
}

/**
 * Base64 URL encode (RFC 4648)
 */
function base64UrlEncode(data: string | ArrayBuffer): string {
  let base64: string;

  if (typeof data === 'string') {
    base64 = btoa(data);
  } else {
    const bytes = new Uint8Array(data);
    const binary = Array.from(bytes, (byte) => String.fromCharCode(byte)).join('');
    base64 = btoa(binary);
  }

  // Convert to URL-safe base64
  return base64.replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
}

/**
 * Base64 decode
 */
function base64Decode(base64: string): ArrayBuffer {
  const binary = atob(base64);
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i++) {
    bytes[i] = binary.charCodeAt(i);
  }
  return bytes.buffer;
}
