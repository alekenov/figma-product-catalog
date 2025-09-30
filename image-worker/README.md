# Flower Shop Image Worker

Cloudflare Worker для загрузки и хранения изображений товаров в R2 storage с автоматическим CDN кешированием.

## 🎯 Возможности

- ✅ Загрузка изображений через multipart/form-data
- ✅ Автоматическое генерирование уникальных ID
- ✅ Хранение в Cloudflare R2 (S3-compatible)
- ✅ CDN кеширование с max-age 1 год
- ✅ CORS для всех доменов
- ✅ Валидация типов файлов (jpeg, png, webp, gif)
- ✅ Ограничение размера файлов (макс 10MB)

## 📦 Установка

```bash
npm install
```

## 🚀 Deployment

### 1. Login to Cloudflare

```bash
npx wrangler login
```

### 2. Create R2 Bucket (если еще не создан)

```bash
npx wrangler r2 bucket create flower-shop-images
```

### 3. Deploy Worker

```bash
npx wrangler deploy
```

Worker будет доступен по адресу:
**https://flower-shop-images.{your-account}.workers.dev**

## 📚 API Endpoints

### Health Check

```bash
GET /
```

**Response:**
```json
{
  "status": "ok",
  "service": "flower-shop-images",
  "version": "1.0.0"
}
```

### Upload Image

```bash
POST /upload
Content-Type: multipart/form-data

file: <image file>
```

**Response:**
```json
{
  "success": true,
  "imageId": "mg65z9dq-y2nimv34jn.png",
  "url": "https://flower-shop-images.alekenov.workers.dev/mg65z9dq-y2nimv34jn.png",
  "size": 67890,
  "type": "image/png"
}
```

### Get Image

```bash
GET /{imageId}
```

**Response:** Image binary data with headers:
- `Content-Type`: image/jpeg, image/png, etc.
- `Cache-Control`: public, max-age=31536000, immutable
- `ETag`: {etag}

### Debug (список загруженных файлов)

```bash
GET /debug
```

**Response:**
```json
{
  "success": true,
  "objects": [
    {
      "key": "mg65z9dq-y2nimv34jn.png",
      "size": 67890,
      "uploaded": "2025-09-30T06:14:52.955Z"
    }
  ],
  "truncated": false
}
```

## 🧪 Testing

### Test Upload

```bash
curl -X POST "https://flower-shop-images.alekenov.workers.dev/upload" \
  -F "file=@path/to/your/image.png"
```

### Test Download

```bash
curl "https://flower-shop-images.alekenov.workers.dev/{imageId}" \
  --output downloaded-image.png
```

## 🔧 Configuration

### wrangler.toml

```toml
name = "flower-shop-images"
main = "src/index.ts"
compatibility_date = "2024-09-30"
compatibility_flags = ["nodejs_compat"]

[[r2_buckets]]
binding = "IMAGES"
bucket_name = "flower-shop-images"
```

### Environment Variables

Настройте в проекте frontend/website:

```env
VITE_IMAGE_WORKER_URL=https://flower-shop-images.alekenov.workers.dev
```

## 📝 Frontend Integration

```javascript
// Upload image
const formData = new FormData();
formData.append('file', file);

const response = await fetch(`${VITE_IMAGE_WORKER_URL}/upload`, {
  method: 'POST',
  body: formData,
});

const result = await response.json();
console.log('Uploaded:', result.url);

// Display image
<img src={result.url} alt="Product" loading="lazy" />
```

## 🔒 Security

- Валидация типов файлов (только изображения)
- Ограничение размера (макс 10MB)
- Sanitization путей для предотвращения path traversal
- CORS настроен для безопасного доступа

## 💰 Pricing (Cloudflare R2)

- **Storage**: $0.015 / GB месяц
- **Class A Operations** (uploads): $4.50 / million
- **Class B Operations** (downloads): $0.36 / million
- **Egress Traffic**: **БЕСПЛАТНО** ⭐

Для магазина с 1000 товаров по 100KB каждый:
- Storage: ~$0.0015/месяц
- 10,000 uploads: ~$0.045
- 100,000 downloads: **$0** (egress бесплатно!)

**Итого:** ~$0.05/месяц 🎉

## 📊 Monitoring

### View Real-time Logs

```bash
npx wrangler tail
```

### Check R2 Storage

```bash
npx wrangler r2 object get flower-shop-images/{imageId}
```

## 🛠️ Development

### Run Locally

```bash
npx wrangler dev
```

Worker будет доступен на http://localhost:8787

## 🔄 Updates

После изменения кода:

```bash
npx wrangler deploy
```

## 📞 Support

- [Cloudflare Workers Docs](https://developers.cloudflare.com/workers/)
- [Cloudflare R2 Docs](https://developers.cloudflare.com/r2/)
- [Wrangler CLI Docs](https://developers.cloudflare.com/workers/wrangler/)