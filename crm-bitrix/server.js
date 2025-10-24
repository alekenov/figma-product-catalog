/**
 * Node.js proxy server for Railway deployment
 * Proxies /api/v2/* requests to cvety.kz/api/v2/* to avoid CORS
 * Serves static files from dist/ for all other requests
 */

import express from 'express';
import fetch from 'node-fetch';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

const app = express();
const PORT = process.env.PORT || 8080;

const BITRIX_API_URL = 'https://cvety.kz/api/v2';
const BITRIX_TOKEN = process.env.VITE_BITRIX_TOKEN || 'ABE7142D-D8AB-76AF-8D6C-2C4FAEA9B144';
const BITRIX_CITY = process.env.VITE_BITRIX_CITY || 'astana';

// Parse JSON bodies
app.use(express.json());

// CORS middleware for all requests
app.use((req, res, next) => {
  res.header('Access-Control-Allow-Origin', '*');
  res.header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS, PATCH');
  res.header('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-City');
  res.header('Access-Control-Max-Age', '3600');

  // Handle preflight
  if (req.method === 'OPTIONS') {
    return res.sendStatus(204);
  }
  next();
});

// API proxy middleware
app.use('/api/v2', async (req, res) => {
  const apiPath = req.path;
  const apiUrl = `${BITRIX_API_URL}${apiPath}${req.url.includes('?') ? req.url.substring(req.url.indexOf('?')) : ''}`;

  console.log(`[Proxy] ${req.method} ${apiUrl}`);

  try {
    const headers = {
      'Authorization': `Bearer ${BITRIX_TOKEN}`,
      'X-City': req.headers['x-city'] || BITRIX_CITY,
    };

    // Only add Content-Type for non-GET requests
    if (req.method !== 'GET') {
      headers['Content-Type'] = 'application/json';
    }

    const response = await fetch(apiUrl, {
      method: req.method,
      headers,
      body: req.method !== 'GET' ? JSON.stringify(req.body) : undefined,
    });

    const contentType = response.headers.get('content-type');

    // Forward response
    res.status(response.status);

    if (contentType && contentType.includes('application/json')) {
      const data = await response.json();
      res.json(data);
    } else {
      const text = await response.text();
      res.send(text);
    }
  } catch (error) {
    console.error('[Proxy Error]', error);
    res.status(500).json({
      success: false,
      error: `API request failed: ${error.message}`,
    });
  }
});

// Serve static files from dist/
app.use(express.static(path.join(__dirname, 'dist')));

// SPA fallback - serve index.html for all non-API routes
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'dist', 'index.html'));
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`✅ Server running on http://0.0.0.0:${PORT}`);
  console.log(`📡 Proxying /api/v2/* to ${BITRIX_API_URL}`);
});
